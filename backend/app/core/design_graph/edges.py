from dataclasses import dataclass

@dataclass
class InterfaceEdge:
    source: str
    target: str
    signal: str