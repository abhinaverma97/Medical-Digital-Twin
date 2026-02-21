from graphviz import Digraph


class SystemDiagramGenerator:
    """
    Generates professional system architecture diagrams
    from a DesignGraph.
    """

    def __init__(self, design_graph):
        self.graph = design_graph

    def generate(self, output_path: str, format: str = "png"):
        """
        output_path: path without extension
        format: png | svg | pdf
        """

        dot = Digraph(
            name=self.graph.device_name,
            format=format,
            graph_attr={
                "rankdir": "LR",          # Left → Right flow
                "splines": "ortho",       # Clean orthogonal lines
                "nodesep": "1",
                "ranksep": "1.2"
            },
            node_attr={
                "shape": "box",
                "style": "rounded,filled",
                "fillcolor": "#E8F0FE",
                "fontname": "Helvetica",
                "fontsize": "10"
            },
            edge_attr={
                "fontname": "Helvetica",
                "fontsize": "9"
            }
        )

        # 1. Add subsystem nodes
        for subsystem_name in self.graph.subsystems:
            dot.node(
                name=subsystem_name,
                label=self._format_subsystem_label(subsystem_name)
            )

        # 2. Add interface edges
        for interface in self.graph.interfaces:
            dot.edge(
                interface.source,
                interface.target,
                label=interface.signal
            )

        # 3. Render diagram
        dot.render(output_path, cleanup=True)

        return f"{output_path}.{format}"

    def _format_subsystem_label(self, subsystem_name: str) -> str:
        """
        Creates a clean, engineering-style label.
        """
        return f"<<b>{subsystem_name}</b>>"