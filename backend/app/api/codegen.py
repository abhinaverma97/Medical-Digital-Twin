from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..core.codegen.generator import CodeGenerator
from .requirements import store
from . import design as design_module
import os
import io
import zipfile
import tempfile

router = APIRouter()

@router.get("/download-zip/")
def download_code_zip():
    """
    Generates the code repository in-memory and returns it as a
    downloadable ZIP file. No files are written to disk.
    """
    if design_module.design_graph is None:
        raise HTTPException(
            status_code=400,
            detail="Design graph not built. Call POST /design/build first."
        )

    design_graph = design_module.design_graph
    requirements = store.get_all()

    device_name = design_graph.get("device_name", "medical_device") if isinstance(design_graph, dict) else design_graph.device_name
    device_slug = device_name.lower().replace(" ", "_")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, "..", "core", "codegen", "templates")

    generator = CodeGenerator(template_dir)

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = os.path.join(tmp_dir, device_slug)
            generator.generate_repo(design_graph, requirements, output_dir)

            # Zip the generated directory into an in-memory buffer
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(output_dir):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        # Archive path is relative to the temp dir so the zip
                        # contains a top-level folder named after the device
                        arcname = os.path.relpath(abs_path, tmp_dir)
                        zf.write(abs_path, arcname)
            zip_buffer.seek(0)

            zip_filename = f"{device_slug}_codebase.zip"
            return StreamingResponse(
                io.BytesIO(zip_buffer.read()),
                media_type="application/zip",
                headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Codegen Error: {str(e)}")

