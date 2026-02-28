// designToHWConfig.js — Hardware Twin always uses its hand-crafted static config.
//
// The static HardwareTwinConfig contains carefully positioned electronics blocks,
// bus routing, and power domains that form a proper schematic. The AI-generated
// design details (ComponentsTable, PowerTree, InterfaceMap) are too unpredictable
// to reliably produce a correct electronics-level diagram.
//
// We keep this module so the import in HardwareTwin.jsx doesn't break,
// but it simply returns the static fallback config.

import { HW_CONFIGS } from './HardwareTwinConfig';

/**
 * Returns the static HW config for the given device.
 * Design data is intentionally NOT used to override the electronics schematic —
 * the hand-crafted configs have precise block positions, bus routing, and
 * power domain overlays that cannot be auto-generated reliably.
 */
export function buildHWConfigFromDesign(deviceKey, _designData) {
    return HW_CONFIGS[deviceKey];
}
