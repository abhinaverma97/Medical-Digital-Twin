from fastapi import APIRouter, HTTPException
from ..core.requirements.schema import Requirement
from ..core.requirements.validator import validate_requirement
from ..core.requirements.store import RequirementStore

router = APIRouter()
store = RequirementStore()

@router.post("/")
def add_requirement(req: Requirement):
    print(f"DEBUG: Incoming requirement: {req.id} ({req.type})")
    errors = validate_requirement(req)
    if errors:
        print(f"DEBUG: Validation errors for {req.id}: {errors}")
        raise HTTPException(status_code=400, detail=errors)
    store.add(req)
    return {"status": "added", "id": req.id}

@router.get("/")
def get_requirements():
    return store.get_all()