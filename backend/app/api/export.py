from fastapi import APIRouter, HTTPException
from ..core.compliance.gate import ComplianceGate
from ..core.traceability.matrix import TraceabilityMatrix
from .requirements import store
# Import modules (not values) so we always read the current module-level
# state after /design/build and /simulation/run have executed.
from . import design as design_module
from . import simulation as simulation_module

router = APIRouter()


def _require_design_graph():
    """Guard: raises 400 if /design/build has not been called yet."""
    if design_module.design_graph is None:
        raise HTTPException(
            status_code=400,
            detail="Design graph has not been built. Call POST /design/build first."
        )
    return design_module.design_graph


@router.post("/validate")
def validate_design():
    dg = _require_design_graph()
    gate = ComplianceGate()
    return gate.evaluate(
        requirements=store.get_all(),
        design_graph=dg,
        simulation_snapshots=simulation_module.simulation_results
    )


@router.get("/traceability")
def traceability():
    dg = _require_design_graph()
    reqs = store.get_all()
    # Compute compliance report inline; do NOT call POST validate_design()
    # (a GET endpoint must not trigger side-effecting POST logic)
    gate = ComplianceGate()
    compliance_report = gate.evaluate(
        requirements=reqs,
        design_graph=dg,
        simulation_snapshots=simulation_module.simulation_results
    )
    matrix = TraceabilityMatrix(reqs, dg, compliance_report)
    return matrix.generate()