from fastapi import APIRouter
from ..core.simulation.class2.ventilator import VentilatorTwin
from ..core.simulation.class1.pulse_oximeter import PulseOximeterTwin
from ..core.simulation.class3.dialysis import DialysisTwin
from ..core.simulation.engine import SimulationEngine
from ..core.simulation.faults import FaultInjector
from .requirements import store

router = APIRouter()
simulation_results = []


def _extract_ventilator_params(requirements) -> dict:
    """
    Derives simulation parameters from structured requirements.
    Walks all performance and safety requirements and extracts:
      - target_flow_rate : first performance req for FlowRate with a midpoint
      - max_flow_rate    : max_value of the flow-rate performance req
      - max_pressure     : max_value of the pressure safety req

    Falls back to safe device-class defaults if requirements are not yet
    loaded or the relevant fields are absent.
    """
    params = {
        "target_flow_rate": 30.0,   # L/min default
        "max_flow_rate":    60.0,   # L/min default
        "max_pressure":     40.0,   # cmH2O default (IEC 80601-2-12)
    }

    for req in requirements:
        if req.type == "performance" and req.parameter:
            param_lower = req.parameter.lower()
            if "flow" in param_lower:
                if req.max_value is not None:
                    params["max_flow_rate"] = req.max_value
                if req.min_value is not None and req.max_value is not None:
                    # Target = midpoint of operating range
                    params["target_flow_rate"] = (
                        req.min_value + req.max_value
                    ) / 2.0

        if req.type == "safety" and req.parameter:
            param_lower = req.parameter.lower()
            if "pressure" in param_lower and req.max_value is not None:
                params["max_pressure"] = req.max_value

    return params


def _extract_pulse_ox_params(requirements) -> dict:
    """
    Derives SpO2 and Pulse Rate parameters from requirements.
    """
    params = {
        "target_spo2": 98.0,
        "min_spo2":    90.0,
        "target_hr":   70.0,
        "max_hr":      120.0,
    }

    for req in requirements:
        if req.type == "performance" and req.parameter:
            param_lower = req.parameter.lower()
            if "spo2" in param_lower:
                if req.min_value is not None and req.max_value is not None:
                    params["target_spo2"] = (req.min_value + req.max_value) / 2.0
            elif "pulse" in param_lower or "hr" in param_lower:
                if req.min_value is not None and req.max_value is not None:
                    params["target_hr"] = (req.min_value + req.max_value) / 2.0

        if req.type == "safety" and req.parameter:
            param_lower = req.parameter.lower()
            if "spo2" in param_lower and req.min_value is not None:
                params["min_spo2"] = req.min_value
            elif ("pulse" in param_lower or "hr" in param_lower) and req.max_value is not None:
                params["max_hr"] = req.max_value

    return params


def _extract_dialysis_params(requirements):
    params = {}
    for req in requirements:
        if req.id == "REQ-DIAL-002":
            params["target_bfr"] = (req.min_value + req.max_value) / 2
        if req.id == "REQ-DIAL-003":
            params["max_tmp"] = req.max_value
    return params


TWIN_MAP = {
    "ventilator": VentilatorTwin,
    "pulse_ox": PulseOximeterTwin,
    "dialysis": DialysisTwin
}

PARAM_EXTRACTOR_MAP = {
    "ventilator": _extract_ventilator_params,
    "pulse_ox": _extract_pulse_ox_params,
    "dialysis": _extract_dialysis_params
}


@router.post("/run")
def run_simulation(steps: int = 10, device_type: str = "ventilator", fidelity: str = "L2"):
    """
    Runs a Digital Twin simulation of the specified device.
    """
    global simulation_results

    device_type = device_type.lower()
    twin_class = TWIN_MAP.get(device_type)
    extractor = PARAM_EXTRACTOR_MAP.get(device_type)

    if not twin_class or not extractor:
        return {"error": f"Device type {device_type} not supported"}

    params = extractor(store.get_all())
    params["fidelity"] = fidelity
    twin = twin_class(**params)
    
    engine = SimulationEngine(twin)
    simulation_results = engine.run(steps)

    return {
        "parameters_used": params,
        "steps": steps,
        "snapshots": simulation_results
    }


@router.post("/fault")
def run_faulty_simulation(
    parameter: str,
    bias: float,
    steps: int = 10,
    device_type: str = "ventilator",
    fidelity: str = "L2"
):
    """
    Injects a fault into the simulation for safety/what-if analysis.
    bias: e.g. 0.2 means +20% sensor bias.
    """
    global simulation_results

    device_type = device_type.lower()
    twin_class = TWIN_MAP.get(device_type)
    extractor = PARAM_EXTRACTOR_MAP.get(device_type)

    if not twin_class or not extractor:
        return {"error": f"Device type {device_type} not supported"}

    params = extractor(store.get_all())
    params["fidelity"] = fidelity
    twin = twin_class(**params)
    
    # Apply Fault
    injector = FaultInjector(twin)
    try:
        injector.apply_sensor_bias(parameter, bias)
    except ValueError as e:
        return {"error": str(e)}

    engine = SimulationEngine(twin)
    simulation_results = engine.run(steps)

    return {
        "status": "fault_injected",
        "fault": {"parameter": parameter, "bias": bias},
        "parameters_used": params,
        "snapshots": simulation_results
    }