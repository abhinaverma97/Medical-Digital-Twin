from graphviz import Digraph


class HLDGenerator:
    """
    Generates a High-Level Design diagram deterministically
    from a DesignGraph. All nodes and edges are derived from
    the graph, which in turn was built from structured requirements.
    Nothing is hardcoded.
    """

    def __init__(self, design_graph):
        self.graph = design_graph

    def build(self) -> Digraph:
        dot = Digraph(
            "HLD",
            graph_attr={
                "rankdir": "LR",
                "splines": "ortho",
                "nodesep": "0.8",
                "ranksep": "1.5",
                "fontname": "Helvetica"
            },
            node_attr={
                "fontname": "Helvetica",
                "fontsize": "10"
            },
            edge_attr={
                "fontname": "Helvetica",
                "fontsize": "9",
                "color": "#4A4A4A"
            }
        )
        dot.attr(
            label=f"{self.graph.device_name} - High-Level System Design",
            labelloc="t",
            fontsize="14",
            fontname="Helvetica-Bold"
        )

        # System boundary cluster
        with dot.subgraph(name="cluster_system") as system:
            system.attr(
                label=f"{self.graph.device_name} System Boundary",
                style="rounded,dashed",
                color="black",
                fontsize="12"
            )

            for name, node in self.graph.subsystems.items():
                label = self._build_subsystem_label(name, node)
                system.node(
                    name,
                    label=label,
                    shape="box",
                    style="rounded,filled",
                    fillcolor="#E8F0FE",
                    color="#4A90D9"
                )

        # Interface edges — derived from interface requirements via graph
        drawn = set()
        for iface in self.graph.interfaces:
            key = (iface.source, iface.target, iface.signal)
            if key not in drawn:
                dot.edge(
                    iface.source,
                    iface.target,
                    label=f"  {iface.signal}  ",
                    color="#4A90D9"
                )
                drawn.add(key)

        return dot

    def _build_subsystem_label(self, name: str, node) -> str:
        """
        Builds an HTML-like label from the subsystem's requirement-derived
        inputs and outputs. No hardcoded content.
        """
        # Sanitized name for HTML display
        safe_name = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        rows = [f'<table border="0" cellborder="0" cellspacing="2">']
        rows.append(f'<tr><td><b>{safe_name}</b></td></tr>')

        if node.outputs:
            for out in node.outputs:
                safe_out = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                rows.append(
                    f'<tr><td align="left"><font color="#1a6b1a" point-size="9">-&gt; {safe_out}</font></td></tr>'
                )

        if node.inputs:
            for inp in node.inputs:
                safe_inp = inp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                rows.append(
                    f'<tr><td align="left"><font color="#7a3b00" point-size="9">&lt;- {safe_inp}</font></td></tr>'
                )

        rows.append('</table>')
        # Wrap in < > so the graphviz library produces << ... >> in the DOT file
        return "<" + "".join(rows) + ">"