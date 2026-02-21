class TraceabilityMatrix:
    """
    Generates a full REQ → Design → Risk → Verification → Evidence
    traceability matrix.

    Columns produced:
      Requirement ID | Priority | Status | Type | Title | Subsystem |
      Parent ID | Design Element | Hazard | Risk Acceptability |
      Risk Status | Verification Method | Verification Description |
      Evidence
    """

    _EVIDENCE_MAP = {
        "simulation":  "Digital Twin Simulation Logs",
        "analysis":    "Design Analysis Report",
        "inspection":  "Inspection Checklist",
        "test":        "Test Case Execution Record",
    }

    def __init__(self, requirements, design_graph, compliance_report):
        self.requirements       = requirements
        self.design_graph       = design_graph
        self.compliance_report  = compliance_report

        # Build a fast lookup: req_id → risk register entry (ISO 14971)
        self._risk_index = self._build_risk_index()

    def generate(self) -> list[dict]:
        matrix = []
        for req in self.requirements:
            risk = self._risk_index.get(req.id, {})
            row = {
                "Requirement ID":           req.id,
                "Priority":                 req.priority,
                "Status":                   req.status,
                "Type":                     req.type,
                "Title":                    req.title,
                "Subsystem":                req.subsystem or "—",
                "Parent ID":                req.parent_id or "—",
                "Design Element":           self._resolve_design(req),
                "Hazard":                   req.hazard or "N/A",
                "Severity":                 req.severity or "N/A",
                "Probability":              req.probability or "N/A",
                "Risk Acceptability":       risk.get("risk_acceptability", "N/A"),
                "Risk Status":              risk.get("risk_status", "N/A"),
                "Verification Method":      req.verification.method,
                "Verification Description": req.verification.description,
                "Evidence":                 self._EVIDENCE_MAP.get(
                                                req.verification.method, "N/A"
                                            ),
            }
            matrix.append(row)
        return matrix

    # ── helpers ────────────────────────────────────────────────────────────

    def _build_risk_index(self) -> dict:
        """
        Indexes the ISO 14971 risk register (from the compliance report)
        by requirement_id for O(1) lookup during matrix generation.
        """
        index = {}
        for result in self.compliance_report.get("results", []):
            if result.get("standard") == "ISO 14971":
                for entry in result.get("details", []):
                    req_id = entry.get("requirement_id")
                    if req_id:
                        index[req_id] = entry
        return index

    def _resolve_design(self, req) -> str:
        """Maps a requirement to its design graph element (if built)."""
        if req.type == "interface":
            return f"Interface: {req.interface}"
        if self.design_graph and req.subsystem in self.design_graph.subsystems:
            return f"Subsystem node: {req.subsystem}"
        return f"Subsystem: {req.subsystem or '—'}"