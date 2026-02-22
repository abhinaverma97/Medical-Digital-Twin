from graphviz import Digraph


class HLDGenerator:
    """
    Generates a High-Level Design diagram with robust component visibility.
    Industry-grade styling.
    """

    def __init__(self, design_graph):
        self.graph = design_graph

    def build(self) -> Digraph:
        dot = Digraph(
            "HLD",
            graph_attr={
                "rankdir": "LR",
                "splines": "ortho",
                "nodesep": "1.0",
                "ranksep": "1.5",
                "fontname": "Helvetica",
                "bgcolor": "#F8FAFC",
                "size": "10,8!",
                "ratio": "fill"
            },

            node_attr={"fontname": "Helvetica", "fontsize": "10"},
            edge_attr={"fontname": "Helvetica", "fontsize": "9", "color": "#475569"}
        )
        dot.attr(
            label=f"{self.graph.device_name} - High-Level System Design",
            labelloc="t",
            fontsize="16",
            fontname="Helvetica-Bold",
            fontcolor="#0F172A"
        )

        with dot.subgraph(name="cluster_system") as system:
            system.attr(
                label=f"{self.graph.device_name} Architecture Boundary",
                style="rounded,dashed",
                color="#64748B",
                fontsize="12",
                fontcolor="#64748B"
            )

            for name, node in self.graph.subsystems.items():
                label = self._build_subsystem_label(name, node)
                fill = "#F1F5F9"
                if "Control" in name or "Safety" in name:
                    fill = "#F0F9FF" # Light Blue
                elif "Power" in name:
                    fill = "#FFF7ED" # Light Orange
                
                system.node(
                    name,
                    label=label,
                    shape="box",
                    style="rounded,filled",
                    fillcolor=fill,
                    color="#1E293B"
                )

        drawn = set()
        for iface in self.graph.interfaces:
            key = (iface.source, iface.target, iface.signal)
            if key not in drawn:
                dot.edge(
                    iface.source,
                    iface.target,
                    label=f"  {iface.signal}  ",
                    color="#3B82F6",
                    penwidth="1.2"
                )
                drawn.add(key)

        return dot

    def _build_subsystem_label(self, name: str, node) -> str:
        safe_name = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        rows = [f'<table border="0" cellborder="0" cellspacing="4" cellpadding="2">']
        rows.append(f'<tr><td align="center"><b><font point-size="11">{safe_name}</font></b></td></tr>')

        if node.outputs:
            rows.append('<tr><td align="left">')
            for out in node.outputs:
                safe_out = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                rows.append(f'<font color="#059669" point-size="9">-&gt; {safe_out}</font><br/>')
            rows.append('</td></tr>')


        if node.components:
            rows.append('<tr><td border="1" sides="t"><font point-size="2"> </font></td></tr>')
            rows.append('<tr><td align="left"><b><font point-size="8" color="#475569">Physical Components:</font></b></td></tr>')
            for comp in node.components:
                safe_comp = comp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                rows.append(f'<tr><td align="left"><font color="#1E293B" point-size="8">  - {safe_comp}</font></td></tr>')


        if node.software_stack:
            rows.append('<tr><td border="1" sides="t"><font point-size="2"> </font></td></tr>')
            rows.append('<tr><td align="left"><b><font point-size="8" color="#7C3AED">Software Layer:</font></b></td></tr>')
            for sw in node.software_stack:
                safe_sw = sw['name'].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                rows.append(f'<tr><td align="left"><font color="#1E293B" point-size="8">  [{sw["layer"]}] {safe_sw}</font></td></tr>')

        rows.append('</table>')
        return "<" + "".join(rows) + ">"