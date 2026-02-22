from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class SubsystemNode:
    name: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    # Minute details for components in this subsystem
    detailed_components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Software stack layers for this subsystem
    software_stack: List[Dict[str, str]] = field(default_factory=list)