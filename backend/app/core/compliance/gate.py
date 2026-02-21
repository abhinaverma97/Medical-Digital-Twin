from .base import ComplianceResult
from .iso_14971 import ISO14971RiskEngine
from .iso_60601 import ISO60601SafetyChecks
from .iso_62366 import ISO62366UsabilityChecks


class ComplianceGate:
    """
    Orchestrates all compliance checks and returns a structured gate report.

    Checks executed (in order):
      ISO 14971:2019  — risk management (hazard × probability → risk register)
      ISO 60601-1     — essential performance and safety architecture
      ISO 62366-1     — usability engineering / interface specification

    The gate FAILS if any individual check fails.
    The gate will NOT run ISO 60601-1 checks when design_graph is None
    (i.e. before /design/build has been called) and will include a
    clear diagnostic in the result.
    """

    def evaluate(self, requirements, design_graph, simulation_snapshots):
        results = []

        # ── ISO 14971 — Risk Management ────────────────────────────────
        iso14971 = ISO14971RiskEngine()
        status_14971, details_14971 = iso14971.evaluate(
            requirements, simulation_snapshots
        )
        results.append(
            ComplianceResult("ISO 14971", status_14971, details_14971)
        )

        # ── ISO 60601-1 — Essential Performance & Safety Architecture ──
        if design_graph is None:
            results.append(ComplianceResult(
                "ISO 60601-1",
                "NOT_RUN",
                ["Design graph not built. Call POST /design/build before validation."]
            ))
        else:
            iso60601 = ISO60601SafetyChecks()
            status_60601, details_60601 = iso60601.evaluate(
                design_graph, requirements
            )
            results.append(
                ComplianceResult("ISO 60601-1", status_60601, details_60601)
            )

        # ── ISO 62366-1 — Usability Engineering ───────────────────────
        iso62366 = ISO62366UsabilityChecks()
        status_62366, details_62366 = iso62366.evaluate(requirements)
        results.append(
            ComplianceResult("ISO 62366-1", status_62366, details_62366)
        )

        runnable = [r for r in results if r.status != "NOT_RUN"]
        overall_status = (
            "PASS" if all(r.status == "PASS" for r in runnable) else "FAIL"
        )

        return {
            "overall_status": overall_status,
            "results": [r.to_dict() for r in results]
        }