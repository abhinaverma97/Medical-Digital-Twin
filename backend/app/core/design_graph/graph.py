from .nodes import SubsystemNode
from .edges import InterfaceEdge

class DesignGraph:
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.subsystems = {}
        self.interfaces = []

    def add_subsystem(self, node: SubsystemNode):
        self.subsystems[node.name] = node

    def connect(self, source: str, target: str, signal: str):
        self.interfaces.append(
            InterfaceEdge(source, target, signal)
        )

    def to_dict(self):
        return {
            "device": self.device_name,
            "subsystems": list(self.subsystems.keys()),
            "interfaces": [
                vars(i) for i in self.interfaces
            ]
        }