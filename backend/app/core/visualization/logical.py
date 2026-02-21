from graphviz import Digraph


class LogicalDiagramGenerator:
    """
    Generates a Logical / LLD diagram deterministically from the
    DesignGraph and its associated requirements.

    - Subsystem nodes are derived from DesignGraph.subsystems
    - Signal edges are derived from DesignGraph.interfaces (interface requirements)
    - Performance bands are annotated from performance requirements
    - Safety flags are annotated from safety requirements

    Nothing is hardcoded.
    """

    def __init__(self, design_graph, requirements):
        self.graph = design_graph
        self.reqs = requirements

    def build(self) -> Digraph:
        dot = Digraph(
            "Logical",
            graph_attr={
                "rankdir": "LR",
                "splines": "spline",
                "nodesep": "0.9",
                "ranksep": "1.5",
                "fontname": "Helvetica"
            },
            node_attr={
                "fontname": "Helvetica",
                "fontsize": "10"
            },
            edge_attr={
                "fontname": "Helvetica",
                "fontsize": "9"
            }
        )
        dot.attr(
            label=f"{self.graph.device_name} - Logical / Signal Flow Diagram",
            labelloc="t",
            fontsize="14",
            fontname="Helvetica-Bold"
        )

        # 1. Subsystem nodes — fully derived from the graph
        for name, node in self.graph.subsystems.items():
            label = self._build_logical_label(name, node)
            dot.node(
                name,
                label=label,
                shape="box",
                style="rounded,filled",
                fillcolor="#E3F2FD",
                color="#1565C0"
            )

        # 2. Signal edges — derived from interface requirements via graph
        drawn = set()
        for iface in self.graph.interfaces:
            key = (iface.source, iface.target, iface.signal)
            if key not in drawn:
                dot.edge(
                    iface.source,
                    iface.target,
                    label=f"  {iface.signal}  ",
                    color="#1565C0"
                )
                drawn.add(key)

        # 3. Performance constraints — annotated as side notes
        for req in self.reqs:
            if (
                req.type == "performance"
                and req.subsystem
                and req.parameter
                and req.subsystem in self.graph.subsystems
            ):
                perf_id = f"perf_{req.id}"
                range_str = ""
                if req.min_value is not None and req.max_value is not None:
                    unit = req.unit or ""
                    range_str = f"\n[{req.min_value}–{req.max_value} {unit}]"
                elif req.response_time_ms is not None:
                    range_str = f"\n[≤{req.response_time_ms} ms]"

                dot.node(
                    perf_id,
                    label=f"{req.parameter}{range_str}",
                    shape="note",
                    style="filled",
                    fillcolor="#FFF9C4",
                    fontsize="8",
                    color="#F9A825"
                )
                dot.edge(
                    req.subsystem,
                    perf_id,
                    style="dashed",
                    arrowhead="none",
                    color="#F9A825"
                )

        # 4. Safety annotations — flag high/critical hazards on subsystems
        for req in self.reqs:
            if (
                req.type == "safety"
                and req.severity in ("High", "Critical")
                and req.subsystem
                and req.subsystem in self.graph.subsystems
            ):
                safety_id = f"safety_{req.id}"
                # Remove Unicode and ensure no raw newlines in labels
                safe_hazard = req.hazard.replace("\n", " ")
                dot.node(
                    safety_id,
                    label=f"! {safe_hazard}\n({req.severity})",
                    shape="diamond",
                    style="filled",
                    fillcolor="#FFCDD2",
                    fontsize="8",
                    color="#C62828"
                )
                dot.edge(
                    req.subsystem,
                    safety_id,
                    style="dashed",
                    arrowhead="none",
                    color="#C62828"
                )

        return dot

    def _build_logical_label(self, name: str, node) -> str:
        """
        Builds an HTML-like label showing the subsystem name and
        its requirement-derived input/output signals.
        """
        # Sanitized name for HTML display
        safe_name = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        rows = [f'<table border="0" cellborder="0" cellspacing="2">']
        rows.append(f'<tr><td><b>{safe_name}</b></td></tr>')

        if node.inputs:
            safe_inputs = [i.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for i in node.inputs]
            rows.append(
                '<tr><td align="left"><font color="#7a3b00" point-size="8">'
                + "  ".join(f"&lt;- {i}" for i in safe_inputs)
                + "</font></td></tr>"
            )
        if node.outputs:
            safe_outputs = [o.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for o in node.outputs]
            rows.append(
                '<tr><td align="left"><font color="#1a6b1a" point-size="8">'
                + "  ".join(f"-&gt; {o}" for o in safe_outputs)
                + "</font></td></tr>"
            )

        rows.append("</table>")
        # Wrap in < > so the graphviz library produces << ... >> in the DOT file
        return "<" + "".join(rows) + ">"