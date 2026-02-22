from graphviz import Digraph


class LLDGenerator:
    """
    Generates a Low-Level Design (LLD) diagram showing minute engineering details:
    - Component models (MCUs, Sensors, Actuators)
    - Communication Bus hierarchies (CAN, I2C, SPI)
    - Protocol specifications
    """

    def __init__(self, design_graph):
        self.graph = design_graph

    def build(self) -> Digraph:
        dot = Digraph(
            "LLD",
            graph_attr={
                "rankdir": "LR", 
                "splines": "polyline",
                "nodesep": "1.0",
                "ranksep": "1.5",
                "fontname": "Courier",
                "compound": "true",
                "bgcolor": "#1E293B",
                "size": "12,10!",
                "ratio": "fill"
            },

            node_attr={
                "fontname": "Courier-Bold",
                "fontsize": "9",
                "color": "#94A3B8",
                "fontcolor": "#F8FAFC"
            },
            edge_attr={
                "fontname": "Courier",
                "fontsize": "8",
                "color": "#38BDF8",
                "fontcolor": "#38BDF8"
            }
        )
        dot.attr(
            label=f"{self.graph.device_name} - Low-Level Engineering Schematic",
            labelloc="t",
            fontsize="16",
            fontname="Courier-Bold",
            fontcolor="#F8FAFC"
        )

        # Draw each subsystem as a cluster with internal components as nodes
        for ss_name, node in self.graph.subsystems.items():
            with dot.subgraph(name=f"cluster_{ss_name}") as subsys:
                subsys.attr(
                    label=ss_name,
                    style="filled",
                    fillcolor="#334155",
                    color="#475569",
                    fontcolor="#38BDF8",
                    fontsize="12"
                )

                # Create nodes for each detailed component
                for comp_name, detail in node.detailed_components.items():
                    comp_id = f"{ss_name}_{comp_name}".replace(" ", "_").replace("(", "").replace(")", "")
                    label = self._build_component_label(comp_name, detail)
                    subsys.node(
                        comp_id,
                        label=label,
                        shape="record",
                        style="filled",
                        fillcolor="#0F172A",
                        color="#38BDF8"
                    )

                # If no detailed components, create a generic placeholder node
                if not node.detailed_components and node.components:
                    for comp in node.components:
                        comp_id = f"{ss_name}_{comp}".replace(" ", "_").replace("(", "").replace(")", "")
                        subsys.node(
                            comp_id,
                            label=comp,
                            shape="box",
                            style="filled",
                            fillcolor="#0F172A"
                        )

        # Draw connections between subsystems based on interfaces
        # Note: In a real LLD, we'd map signals to specific component pins/buses.
        # For this upgraded prototype, we'll connect the "Main MCU" or first available component to mimic connectivity.
        for iface in self.graph.interfaces:
            source_comp = self._get_representative_comp(iface.source)
            target_comp = self._get_representative_comp(iface.target)
            
            if source_comp and target_comp:
                dot.edge(
                    source_comp,
                    target_comp,
                    label=f" {iface.signal} ",
                    penwidth="1.0"
                )

        return dot

    def _build_component_label(self, name: str, detail: dict) -> str:
        rows = [f"{name}"]
        if "model" in detail:
            rows.append(f"Model: {detail['model']}")
        if "bus" in detail:
            rows.append(f"Bus: {detail['bus']}")
        if "interface" in detail:
            rows.append(f"IF: {detail['interface']}")
        if "purpose" in detail:
            rows.append(f"P: {detail['purpose']}")
        
        return " | ".join(rows)

    def _get_representative_comp(self, subsys_name: str) -> str:
        if subsys_name not in self.graph.subsystems:
            return None
        node = self.graph.subsystems[subsys_name]
        
        # Priority 1: MCUs
        for comp_name, detail in node.detailed_components.items():
            if "MCU" in detail.get("type", "") or "Controller" in comp_name:
                return f"{subsys_name}_{comp_name}".replace(" ", "_").replace("(", "").replace(")", "")
        
        # Priority 2: First component
        if node.detailed_components:
            first_comp = list(node.detailed_components.keys())[0]
            return f"{subsys_name}_{first_comp}".replace(" ", "_").replace("(", "").replace(")", "")
        
        # Priority 3: First string component
        if node.components:
            return f"{subsys_name}_{node.components[0]}".replace(" ", "_").replace("(", "").replace(")", "")
        
        return None
