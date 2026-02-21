import os
from fastapi import APIRouter
from ..core.devices.class2.ventilator import Ventilator
from ..core.devices.class1.pulse_oximeter import PulseOximeter
from ..core.devices.class3.dialysis import DialysisMachine
from ..core.design_graph.builder import DesignGraphBuilder
from ..core.visualization.hld import HLDGenerator
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

    # Build design graph
    requirements = store.get_all()
    print(f"DEBUG: Building design for {device_type} with {len(requirements)} requirements")
    
    builder = DesignGraphBuilder(device)
    design_graph = builder.build(requirements)
    
    print(f"DEBUG: Design graph built with {len(design_graph.subsystems)} subsystems: {list(design_graph.subsystems.keys())}")

    # Generate diagrams
    hld = HLDGenerator(design_graph).build()
    logical = LogicalDiagramGenerator(design_graph, requirements).build()
    safety = SafetyDiagramGenerator(requirements).build()

    # Render diagrams
    renderer = DiagramRenderer()
    hld_path = "backend/artifacts/hld"
    logical_path = "backend/artifacts/logical"
    
    # Explicitly request SVG format
    renderer.render(hld, hld_path, format="svg")
    renderer.render(logical, logical_path, format="svg")
    
    def get_svg_or_fallback(base_path, diagram_obj):
        try:
            svg_file = f"{base_path}.svg"
            if os.path.exists(svg_file):
                with open(svg_file, "r") as f:
                    return f.read()
            
            # Fallback if Graphviz isn't installed: return raw DOT source
            # so the user can at least see the engineering logic.
            dot_file = f"{base_path}.dot"
            if os.path.exists(dot_file):
                with open(dot_file, "r") as f:
                    content = f.read()
                    return f"<div style='color: #94a3b8; font-family: monospace; white-space: pre; font-size: 10px; text-align: left; padding: 20px;'>// Graphviz not installed. Showing raw DOT source:<br/><br/>{content}</div>"
            
            return f"<svg><text y='20' fill='red'>Rendering failed. Check backend logs.</text></svg>"
        except Exception as e:
            return f"<svg><text y='20' fill='red'>Error: {str(e)}</text></svg>"

    hld_svg = get_svg_or_fallback(hld_path, hld)
    logical_svg = get_svg_or_fallback(logical_path, logical)

    # Return design graph (API response)
    return {
        "device": device.device_name,
        "subsystems": list(design_graph.subsystems),
        "hld": {"svg": hld_svg},
        "logical": {"svg": logical_svg},
        "interfaces": [
            {
                "source": i.source,
                "target": i.target,
                "signal": i.signal
            } for i in design_graph.interfaces
        ]
    }