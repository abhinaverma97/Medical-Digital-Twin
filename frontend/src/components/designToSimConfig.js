// designToSimConfig.js — Transform design graph data into System Twin config shape
import { DEVICE_CONFIGS } from './SimulatorConfig';

/**
 * Normalize a component entry — design graph API returns {name, category} objects,
 * but the simulator UI expects plain strings.
 */
const normComp = (c) => {
    if (typeof c === 'string') return c;
    if (c && typeof c === 'object' && c.name) return c.name;
    return String(c);
};

/**
 * Builds a System Twin config by merging design graph data with the static fallback.
 *
 * Design data overrides: subsystems (names, components, SVG layout), links (from interfaces).
 * Fallback provides: signals, faultMatrix, safetyRules, scenarios (domain-specific).
 *
 * The function keeps the SAME config shape as DEVICE_CONFIGS so ArchitectureView,
 * ComponentsPanel, TelemetryPanel, and AnalysisPanel all work without changes.
 */
export function buildSimConfigFromDesign(deviceKey, designData) {
    const fallback = DEVICE_CONFIGS[deviceKey];
    if (!designData || !designData.graph) return fallback;

    const { graph } = designData;
    const archNodes = graph.architecture || [];
    const ifaces = graph.interfaces || [];

    if (archNodes.length === 0) return fallback;

    // ── Classify subsystems by role for intelligent layout ─────────────
    const classify = (name) => {
        const n = (typeof name === 'string' ? name : '').toLowerCase();
        if (/safety|watchdog|alarm|guard|monitor/i.test(n)) return 'safety';
        if (/power|supply|battery|psu/i.test(n)) return 'power';
        if (/patient|interface|circuit|display|ui/i.test(n)) return 'output';
        return 'core';
    };

    const roleGroups = { power: [], core: [], output: [], safety: [] };
    archNodes.forEach((node) => {
        const role = classify(node.name || node.id);
        roleGroups[role].push(node);
    });

    // ── Layout: arrange subsystems in a logical flow ──────────────────
    //   Row 1 (y=70):  Safety/Monitor subsystems (shorter blocks)
    //   Row 2 (y=180): Power → Core subsystems → Output/Patient (main flow)
    const subsystems = [];
    const SVG_W = 800;
    const mainRow = [...roleGroups.power, ...roleGroups.core, ...roleGroups.output];
    const safetyRow = roleGroups.safety;

    // Main row layout
    const mainBlockW = 130;
    const mainBlockH = 55;
    const mainGap = 20;
    const mainTotalW = mainRow.length * (mainBlockW + mainGap) - mainGap;
    const mainStartX = Math.max(40, (SVG_W - mainTotalW) / 2);
    const mainY = 180;

    mainRow.forEach((node, i) => {
        subsystems.push({
            id: node.id || node.name,
            label: normComp(node.name || node.id),
            x: mainStartX + i * (mainBlockW + mainGap),
            y: mainY,
            w: mainBlockW,
            h: mainBlockH,
            components: (node.components || []).map(normComp),
        });
    });

    // Safety row layout (above main, centered)
    const safeBlockW = 130;
    const safeBlockH = 45;
    const safeTotalW = safetyRow.length * (safeBlockW + mainGap) - mainGap;
    const safeStartX = Math.max(40, (SVG_W - safeTotalW) / 2);
    const safeY = 70;

    safetyRow.forEach((node, i) => {
        subsystems.push({
            id: node.id || node.name,
            label: normComp(node.name || node.id),
            x: safeStartX + i * (safeBlockW + mainGap),
            y: safeY,
            w: safeBlockW,
            h: safeBlockH,
            components: (node.components || []).map(normComp),
        });
    });

    // ── Build position index for link coordinates ────────────────────
    const posMap = {};
    subsystems.forEach(s => {
        posMap[s.id] = {
            x: s.x, y: s.y, w: s.w, h: s.h,
            cx: s.x + s.w / 2,
            cy: s.y + s.h / 2,
            right: s.x + s.w,
            bottom: s.y + s.h,
        };
    });

    // ── Links from interfaces ────────────────────────────────────────
    const links = [];
    ifaces.forEach((iface) => {
        const src = posMap[iface.source];
        const tgt = posMap[iface.target];
        if (!src || !tgt) return;

        // Determine connection direction
        const sameRow = Math.abs(src.cy - tgt.cy) < 60;
        const srcAbove = src.cy < tgt.cy - 30;
        const srcBelow = src.cy > tgt.cy + 30;

        let x1, y1, x2, y2;
        if (sameRow) {
            // Horizontal: right edge of source → left edge of target (or vice-versa)
            if (src.cx < tgt.cx) {
                x1 = src.right; y1 = src.cy;
                x2 = tgt.x; y2 = tgt.cy;
            } else {
                x1 = src.x; y1 = src.cy;
                x2 = tgt.right; y2 = tgt.cy;
            }
        } else if (srcAbove) {
            // Safety (above) → main (below): bottom center → top center
            x1 = src.cx; y1 = src.bottom;
            x2 = tgt.cx; y2 = tgt.y;
        } else {
            // Main (below) → safety (above): top center → bottom center
            x1 = src.cx; y1 = src.y;
            x2 = tgt.cx; y2 = tgt.bottom;
        }

        links.push({
            from: iface.source,
            to: iface.target,
            label: typeof iface.signal === 'string' ? iface.signal : '',
            x1, y1, x2, y2,
            dashed: /safety|kill|heartbeat|watchdog|trip/i.test(iface.signal || ''),
        });
    });

    // ── Return merged config ─────────────────────────────────────────
    return {
        ...fallback,
        subsystems,
        links,
        // These stay from static config — domain-specific, not auto-generated
        label: fallback.label,
        classLabel: fallback.classLabel,
        signals: fallback.signals,
        faultMatrix: fallback.faultMatrix,
        safetyRules: fallback.safetyRules,
        scenarios: fallback.scenarios,
    };
}
