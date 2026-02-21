import sys
import os
import json

# Add project root to path (assuming run from project root)
sys.path.append(os.getcwd())

from backend.app.api.requirements import add_requirement, store
from backend.app.api.design import build_design
from backend.app.api.simulation import run_simulation
from backend.app.core.requirements.schema import Requirement

def test_pulse_ox_pipeline():
    # 0. Clear store if needed (actually it starts empty in a new process)
    
    # 1. Load Pulse Oximeter requirements
    reqs_file = ".samples/pulse_ox_reqs.json"
    if not os.path.exists(reqs_file):
        print(f"Error: {reqs_file} not found")
        sys.exit(1)

    with open(reqs_file, "r") as f:
        reqs_data = json.load(f)

    print("Adding Pulse Oximeter requirements...")
    for req_dict in reqs_data:
        req = Requirement(**req_dict)
        add_requirement(req)

    # 2. Build design for Pulse Oximeter
    print("\nBuilding Pulse Oximeter design graph...")
    design_result = build_design(device_type="pulse_ox")
    if isinstance(design_result, dict) and "error" in design_result:
        print(f"FAILED: {design_result['error']}")
        sys.exit(1)

    print(f"Subsystems: {design_result['subsystems']}")
    print(f"Interfaces: {len(design_result['interfaces'])}")

    # Verify subsystem count (Pulse Oximeter + 4 subsystems)
    expected_subsystems = ["PulseOximeter", "OpticalSensing", "SignalProcessing", "Display", "Alarms"]
    for sub in expected_subsystems:
        if sub not in design_result['subsystems']:
            print(f"Warning: Expected subsystem {sub} missing")

    # 3. Run simulation for Pulse Oximeter
    print("\nRunning Pulse Oximeter simulation...")
    sim_result = run_simulation(steps=5, device_type="pulse_ox")
    if isinstance(sim_result, dict) and "error" in sim_result:
        print(f"FAILED: {sim_result['error']}")
        sys.exit(1)

    print(f"Parameters: {sim_result['parameters_used']}")
    print(f"Snapshots: {len(sim_result['snapshots'])}")
    last_snapshot = sim_result['snapshots'][-1]
    print(f"Final State: {last_snapshot['values']}")

    # Validation of simulation values
    values = last_snapshot['values']
    if "SpO2(%)" not in values or "PulseRate(bpm)" not in values:
        print("FAILED: Missing SpO2 or Pulse rate in simulation output")
        sys.exit(1)

    print("\nVerification OK")

if __name__ == "__main__":
    test_pulse_ox_pipeline()
