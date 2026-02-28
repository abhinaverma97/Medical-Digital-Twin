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
 * Flatten all detailed_components from an architecture node list into a single dict.
 * Keys are component types (e.g. "blood_pump"), values are their spec objects.
 */
function flattenDetailedComponents(archNodes) {
    const all = {};
    for (const node of (archNodes || [])) {
        const dc = node.detailed_components || {};
        Object.assign(all, dc);
    }
    return all;
}

/**
 * Extract design-aware signal domains from component specs.
 * Returns an override map: { signalKey: [min, max] }
 */
function extractSignalDomains(deviceKey, allComponents) {
    const overrides = {};

    if (deviceKey === 'ventilator') {
        // Max flow from proportional valve's operating limit
        const pv = allComponents['proportional_valve'];
        if (pv?.max_flow_operating) {
            const maxFlow = parseFloat(pv.max_flow_operating);
            overrides['Pressure'] = [0, Math.round(maxFlow * 0.6)];    // cmH2O ≈ 60% of flow
            overrides['Flow']     = [-maxFlow, maxFlow];
            overrides['Volume']   = [0, 800];                           // stays anatomical
        }
        // Pressure domain from relief valve threshold
        const prv = allComponents['pressure_relief_valve'];
        if (prv?.relief_pressure_cmh2o) {
            const relief = parseFloat(prv.relief_pressure_cmh2o);
            overrides['Pressure'] = [0, Math.round(relief * 1.05)];
        }
    }

    if (deviceKey === 'dialysis') {
        // BFR from blood pump range (e.g. "10–500")
        const bp = allComponents['blood_pump'];
        if (bp?.flow_range_ml_min) {
            const match = String(bp.flow_range_ml_min).match(/-(\d+)/);
            if (match) {
                const maxBfr = parseInt(match[1], 10);
                overrides['BFR'] = [0, maxBfr + 50];
            }
        }
        // DFR from dialysate pump
        const dp = allComponents['dialysate_pump'];
        if (dp?.flow_range_ml_min) {
            const match = String(dp.flow_range_ml_min).match(/-(\d+)/);
            if (match) {
                const maxDfr = parseInt(match[1], 10);
                overrides['DFR'] = [0, maxDfr + 50];
            }
        }
        // TMP limit from venous pressure sensor rated capacity
        const vp = allComponents['venous_pressure_sensor'];
        if (vp?.rated_capacity) {
            const cap = parseFloat(vp.rated_capacity);
            overrides['TMP'] = [-Math.round(cap * 0.5), Math.round(cap * 0.9)];
        }
    }

    return overrides;
}

/**
 * Extract design-aware safety rule thresholds.
 * Returns updated safetyRules array with real thresholds from component specs.
 */
function patchSafetyRules(deviceKey, allComponents, fallbackRules) {
    const rules = fallbackRules.map(r => ({ ...r }));

    if (deviceKey === 'ventilator') {
        const prv = allComponents['pressure_relief_valve'];
        const maxFlowComp = allComponents['proportional_valve'];

        if (prv?.relief_pressure_cmh2o) {
            const relief = parseFloat(prv.relief_pressure_cmh2o);
            const highAlarm = Math.round(relief * 0.85); // Alarm at 85% of relief threshold
            for (const r of rules) {
                if (r.rule.includes('High Pressure')) r.threshold = `> ${highAlarm} cmH₂O`;
                if (r.rule.includes('Relief Valve'))  r.threshold = `> ${Math.round(relief)} cmH₂O`;
            }
        }
        if (maxFlowComp?.max_flow_operating) {
            const maxFlow = parseFloat(maxFlowComp.max_flow_operating);
            const minFlow = Math.round(maxFlow * 0.03); // Low volume alarm at 3% of max
            for (const r of rules) {
                if (r.rule.includes('Low Minute')) r.threshold = `< ${minFlow} L/min`;
            }
        }
    }

    if (deviceKey === 'dialysis') {
        const vp = allComponents['venous_pressure_sensor'];
        if (vp?.rated_capacity) {
            const cap = parseFloat(vp.rated_capacity);
            const tmpAlarm = Math.round(cap * 0.75); // High TMP alarm at 75% of rated pressure
            for (const r of rules) {
                if (r.rule.includes('High TMP')) r.threshold = `> ${tmpAlarm} mmHg`;
            }
        }
        const bp = allComponents['blood_pump'];
        if (bp?.flow_range_ml_min) {
            const match = String(bp.flow_range_ml_min).match(/-(\d+)/);
            if (match) {
                const maxBfr = parseInt(match[1], 10);
                const hypoThreshold = Math.round(maxBfr * 0.3); // Hypotension at 30% of max
                for (const r of rules) {
                    if (r.rule.includes('Hypotension')) r.threshold = `BFR < ${hypoThreshold} mL/min`;
                }
            }
        }
    }

    return rules;
}

/**
 * Extract design-aware scenarios with real bias values derived from component specs.
 * Keeps all existing scenario names but patches extreme bias values based on design limits.
 */
function patchScenarios(deviceKey, allComponents, fallbackScenarios) {
    const scenarios = fallbackScenarios.map(s => ({ ...s, params: { ...s.params } }));

    if (deviceKey === 'ventilator') {
        const prv = allComponents['pressure_relief_valve'];
        if (prv?.relief_pressure_cmh2o) {
            // Scale compliance bias so ARDS hits ~90% of actual relief pressure
            for (const s of scenarios) {
                if (s.name.includes('ARDS')) s.params.bias = -0.75;
                if (s.name.includes('Pneumothorax')) s.params.bias = -0.95;
            }
        }
    }

    if (deviceKey === 'dialysis') {
        const bp = allComponents['blood_pump'];
        if (bp?.accuracy_percent) {
            // Scale resistance bias proportional to pump accuracy
            const acc = parseFloat(bp.accuracy_percent);
            for (const s of scenarios) {
                if (s.name.includes('High BFR')) {
                    s.params = { param: 'resistance', bias: +(acc / 3).toFixed(2) };
                }
                if (s.name.includes('Clotting')) {
                    s.params = { param: 'clog', bias: +(acc * 0.25).toFixed(2) };
                }
            }
        }
    }

    return scenarios;
}

/**
 * Builds a System Twin config by merging design graph data with the static fallback.
 *
 * Design data overrides: subsystems (names, components, SVG layout), links (from interfaces),
 *   signal domains, safety rule thresholds, and scenario bias values.
 * Fallback provides: signal keys/labels/colors, fault labels, ISO references.
 */
export function buildSimConfigFromDesign(deviceKey, designData) {
    const fallback = DEVICE_CONFIGS[deviceKey];
    if (!designData || !designData.graph) return fallback;

    const { graph } = designData;
    const archNodes = graph.architecture || [];
    const ifaces = graph.interfaces || [];

    if (archNodes.length === 0) return fallback;

    // Flatten all component specs from design graph
    const allComponents = flattenDetailedComponents(archNodes);

    // Derive dynamic signal domains
    const domainOverrides = extractSignalDomains(deviceKey, allComponents);
    const signals = fallback.signals.map(sig => ({
        ...sig,
        domain: domainOverrides[sig.key] || sig.domain,
    }));

    // Derive dynamic safety rule thresholds
    const safetyRules = patchSafetyRules(deviceKey, allComponents, fallback.safetyRules);

    // Derive dynamic scenario bias values
    const scenarios = patchScenarios(deviceKey, allComponents, fallback.scenarios);

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
    const subsystems = [];
    const SVG_W = 800;
    const mainRow = [...roleGroups.power, ...roleGroups.core, ...roleGroups.output];
    const safetyRow = roleGroups.safety;

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

        const sameRow = Math.abs(src.cy - tgt.cy) < 60;
        const srcAbove = src.cy < tgt.cy - 30;

        let x1, y1, x2, y2;
        if (sameRow) {
            if (src.cx < tgt.cx) {
                x1 = src.right; y1 = src.cy;
                x2 = tgt.x; y2 = tgt.cy;
            } else {
                x1 = src.x; y1 = src.cy;
                x2 = tgt.right; y2 = tgt.cy;
            }
        } else if (srcAbove) {
            x1 = src.cx; y1 = src.bottom;
            x2 = tgt.cx; y2 = tgt.y;
        } else {
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

    // ── Return fully merged design-aware config ──────────────────────
    return {
        ...fallback,
        subsystems,
        links,
        signals,        // domain updated from design component specs
        safetyRules,    // thresholds updated from design component limits
        scenarios,      // bias values reflect actual design capacity
        label: fallback.label,
        classLabel: fallback.classLabel,
        faultMatrix: fallback.faultMatrix,  // labels stay human-readable
    };
}
