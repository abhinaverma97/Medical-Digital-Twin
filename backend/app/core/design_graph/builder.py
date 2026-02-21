from collections import defaultdict
from .graph import DesignGraph
from .nodes import SubsystemNode


class DesignGraphBuilder:
    """
    Builds a DesignGraph deterministically from structured requirements.
    """

    def __init__(self, device):
        self.device = device

    def build(self, requirements):
        """
        requirements: List[Requirement]
        """
        graph = DesignGraph(device_name=self.device.device_name)

        # Step 1: Group requirements by subsystem
        subsystem_requirements = self._group_by_subsystem(requirements)

        # Step 2: Create subsystem nodes
        for subsystem, reqs in subsystem_requirements.items():
            node = self._create_subsystem_node(subsystem, reqs)
            graph.add_subsystem(node)

        # Step 3: Infer interfaces
        self._infer_interfaces(graph, requirements)

        return graph

    def _group_by_subsystem(self, requirements):
        grouped = defaultdict(list)

        for req in requirements:
            if not req.subsystem:
                raise ValueError(
                    f"Requirement {req.id} missing subsystem mapping"
                )
            grouped[req.subsystem].append(req)

        return grouped

    def _create_subsystem_node(self, subsystem, requirements):
        inputs = []
        outputs = []

        for req in requirements:
            if req.type == "interface":
                if req.parameter:
                    inputs.append(req.parameter)
            elif req.type in ["functional", "performance"]:
                if req.parameter:
                    outputs.append(req.parameter)

        return SubsystemNode(
            name=subsystem,
            inputs=list(set(inputs)),
            outputs=list(set(outputs))
        )

    def _infer_interfaces(self, graph, requirements):
        """
        Interface inference is STRICT:
        - Only interface requirements create connections
        """

        for req in requirements:
            if req.type != "interface":
                continue

            if not req.interface:
                raise ValueError(
                    f"Interface requirement {req.id} missing 'interface' mapping"
                )

            source, target = self._parse_interface(req.interface)
            signal = req.parameter or "Generic"

            graph.connect(
                source=source,
                target=target,
                signal=signal
            )

    def _parse_interface(self, interface_str):
        """
        Expected format:
        'SourceSubsystem -> TargetSubsystem'
        """
        try:
            source, target = interface_str.split("->")
            return source.strip(), target.strip()
        except ValueError:
            raise ValueError(
                f"Invalid interface format: {interface_str}"
            )