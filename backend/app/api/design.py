import os
from fastapi import APIRouter
from ..core.devices.class2.ventilator import Ventilator
from ..core.devices.class1.pulse_oximeter import PulseOximeter
from ..core.devices.class3.dialysis import DialysisMachine
from ..core.design_graph.builder import DesignGraphBuilder
from ..core.visualization.hld import HLDGenerator
from ..core.visualization.lld import LLDGenerator
from ..core.visualization.logical import LogicalDiagramGenerator
from ..core.visualization.safety import SafetyDiagramGenerator
from ..core.visualization.renderer import DiagramRenderer
from .requirements import store

router = APIRouter()
design_graph = None

DEVICE_MAP = {
    "ventilator": Ventilator,
    "pulse_ox": PulseOximeter,
    "dialysis": DialysisMachine
}

@router.post("/build")
def build_design(device_type: str = "ventilator"):
    global design_graph
    
    device_class = DEVICE_MAP.get(device_type.lower())
    if not device_class:
        return {"error": f"Device type {device_type} not supported"}
    
    device = device_class()

    # Build design graph (Industry-Grade)
    requirements = store.get_all()
    builder = DesignGraphBuilder(device)
    design_graph = builder.build(requirements)

    # Generate diagrams
    hld = HLDGenerator(design_graph).build()
    lld = LLDGenerator(design_graph).build()
    logical = LogicalDiagramGenerator(design_graph, requirements).build()

    # Render diagrams
    renderer = DiagramRenderer()
    hld_path = "backend/artifacts/hld"
    lld_path = "backend/artifacts/lld"
    logical_path = "backend/artifacts/logical"
    
    renderer.render(hld, hld_path, format="svg")
    renderer.render(lld, lld_path, format="svg")
    renderer.render(logical, logical_path, format="svg")
    
    def get_svg(base_path):
        try:
            svg_file = f"{base_path}.svg"
            if os.path.exists(svg_file):
                with open(svg_file, "r") as f:
                    return f.read()
            return f"<svg><text y='20' fill='red'>Rendering missing: {base_path}</text></svg>"
        except Exception as e:
            return f"<svg><text y='20' fill='red'>Error: {str(e)}</text></svg>"

    hld_svg = get_svg(hld_path)
    lld_svg = get_svg(lld_path)
    logical_svg = get_svg(logical_path)

    return {
        "device": device.device_name,
        "class": device.device_class,
        "subsystems": list(design_graph.subsystems),
        "hld": {"svg": hld_svg},
        "lld": {"svg": lld_svg},
        "logical": {"svg": logical_svg},
        "interfaces": [
            {"source": i.source, "target": i.target, "signal": i.signal} for i in design_graph.interfaces
        ]
    }