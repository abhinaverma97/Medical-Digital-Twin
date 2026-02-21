from graphviz import Digraph


class SafetyDiagramGenerator:
    """
    Generates a Safety Architecture diagram from safety requirements.
    Hazards, severity, mitigations, and standards are all derived
    from the requirement fields — nothing is hardcoded.
    """

    _SEVERITY_COLORS = {
        "Low": "#FFF9C4",
        "Medium": "#FFE0B2",
        "High": "#FFCDD2",
        "Critical": "#EF9A9A"
    }

    def __init__(self, requirements):
        self.reqs = requirements

    def build(self) -> Digraph:
        dot = Digraph(
            "Safety",
            graph_attr={
                "rankdir": "TB",
                "splines": "ortho",
                "nodesep": "0.7",
                "ranksep": "1.2",
                "fontname": "Helvetica"
            },
            node_attr={"fontname": "Helvetica", "fontsize": "10"},
            edge_attr={"fontname": "Helvetica", "fontsize": "9"}
        )
        dot.attr(
            label="Safety & Risk Architecture (ISO 14971)",
            labelloc="t",
            fontsize="14",
            fontname="Helvetica-Bold"
        )

        safety_reqs = [r for r in self.reqs if r.type == "safety" and r.hazard]

        if not safety_reqs:
            dot.node("empty", "No safety requirements defined",
                     shape="plaintext")
            return dot

        for req in safety_reqs:
            h_id = f"H_{req.id}"
            m_id = f"M_{req.id}"
            v_id = f"V_{req.id}"

            severity = req.severity or "Low"
            fill = self._SEVERITY_COLORS.get(severity, "#FFFFFF")

            # Hazard node — derived from req.hazard + severity
            dot.node(
                h_id,
                label=f"Hazard: {req.hazard}\nSeverity: {severity}\n{req.id}",
                shape="box",
                style="filled",
                fillcolor=fill,
                color="#C62828"
            )

            # Mitigation node — derived from req.description (what the system does)
            mitigation_text = self._derive_mitigation(req)
            dot.node(
                m_id,
                label=f"Mitigation:\n{mitigation_text}",
                shape="box",
                style="filled",
                fillcolor="#C8E6C9",
                color="#2E7D32"
            )

            # Verification node — derived from req.verification
            dot.node(
                v_id,
                label=f"Verification:\n{req.verification.method.upper()}\n{req.verification.description}",
                shape="note",
                style="filled",
                fillcolor="#E3F2FD",
                color="#1565C0",
                fontsize="8"
            )

            # Standard label on edge
            standard_label = ""
            if req.standard and req.clause:
                standard_label = f"{req.standard} §{req.clause}"
            elif req.standard:
                standard_label = req.standard

            dot.edge(h_id, m_id, label=standard_label, color="#C62828")
            dot.edge(m_id, v_id, style="dashed", color="#1565C0")

        return dot

    def _derive_mitigation(self, req) -> str:
        """
        Derives mitigation text from requirement description.
        Falls back to verification method if description is missing.
        """
        if req.description:
            # Truncate long descriptions for diagram readability
            text = req.description
            return text if len(text) <= 60 else text[:57] + "..."
        return f"{req.verification.method.capitalize()} verification"