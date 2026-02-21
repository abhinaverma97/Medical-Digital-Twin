from fastapi import APIRouter, HTTPException
from ..core.codegen.generator import CodeGenerator
from .requirements import store
from . import design as design_module
import os

router = APIRouter()

@router.post("/generate/")
def generate_code():
    """
    Generates a deterministic, runnable repository based on the
    current system design and requirements.
    """
    if design_module.design_graph is None:
        raise HTTPException(
            status_code=400,
            detail="Design graph not built. Call POST /design/build first."
        )

    design_graph = design_module.design_graph
    requirements = store.get_all()
    
    # Define output path
    device_slug = design_graph.device_name.lower().replace(" ", "_")
    output_dir = f"generated_repos/{device_slug}"
    
    # Template directory is core/codegen/templates
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, "..", "core", "codegen", "templates")
    
    generator = CodeGenerator(template_dir)
    
    try:
        print(f"DEBUG: Starting code generation in {output_dir}")
        generator.generate_repo(design_graph, requirements, output_dir)
        print("DEBUG: Code generation successful")
    except Exception as e:
        print(f"DEBUG: Code generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Codegen Error: {str(e)}")
    
    return {
        "status": "success",
        "message": f"Code repository generated for {design_graph.device_name}",
        "path": os.path.abspath(output_dir)
    }
