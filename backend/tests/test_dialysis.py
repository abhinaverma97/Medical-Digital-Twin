import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.api.requirements import add_requirement, store
from backend.app.api.design import build_design
from backend.app.api.simulation import run_simulation
from backend.app.core.requirements.schema import Requirement

def test_dialysis_pipeline():
    print("Loading Dialysis requirements...")
    with open(".samples/dialysis_reqs.json", "r") as f:
        reqs = json.load(f)
        for r in reqs:
            add_requirement(Requirement(**r))

    print("Building Dialysis design...")
    design = build_design(device_type="dialysis")
    print(f"Device: {design['device']}")
    print(f"Subsystems: {design['subsystems']}")

    print("\nRunning Dialysis simulation (L3 Fidelity)...")
    sim_result = run_simulation(steps=10, device_type="dialysis", fidelity="L3")
    
    # Final state
    final_state = sim_result['snapshots'][-1]['values']
    print(f"Final State: {final_state}")
    
    # Check if target BFR was reached (approx)
    if final_state['BloodFlowRate(mL/min)'] < 200:
        print("FAILED: Blood flow rate tracking issues")
        sys.exit(1)
        
    print("\nDialysis Pipeline Verification OK")

if __name__ == "__main__":
    test_dialysis_pipeline()
