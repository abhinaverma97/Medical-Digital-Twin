from dataclasses import dataclass
from typing import List

@dataclass
class SubsystemNode:
    name: str
    inputs: List[str]
    outputs: List[str]