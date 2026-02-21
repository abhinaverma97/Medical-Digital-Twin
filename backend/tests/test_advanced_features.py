import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.api.requirements import add_requirement, store
from backend.app.api.design import build_design
from backend.app.api.simulation import run_simulation, run_faulty_simulation
from backend.app.api.codegen import generate_code
from backend.app.api.export import validate_design
from backend.app.core.requirements.schema import Requirement

def test_advanced_features():
    # 1. Setup - Load base Ventilator requirements
    print("Loading Ventilator requirements...")
    samples_dir = ".samples"
    for filename in sorted(os.listdir(samples_dir)):
        if filename.startswith("req") and filename.endswith(".json"):
            with open(os.path.join(samples_dir, filename), "r") as f:
                data = json.load(f)
                add_requirement(Requirement(**data))

    # 2. Build Design
    print("Building Ventilator design...")
    build_design(device_type="ventilator")

    # 3. Test Code Generation API
    print("\nTesting Code Generation API...")
    codegen_result = generate_code()
    print(f"Codegen status: {codegen_result['status']}")
    print(f"Path: {codegen_result['path']}")
    if not os.path.exists(codegen_result['path']):
        print("FAILED: Generated repository path does not exist")
        sys.exit(1)

    # 4. Test L3 Fidelity Simulation
    print("\nTesting L3 Fidelity Simulation...")
    sim_result_l3 = run_simulation(steps=5, device_type="ventilator", fidelity="L3")
    print(f"L3 Snapshot sample: {sim_result_l3['snapshots'][-1]['values']['Pressure(cmH2O)']}")

    sim_result_l2 = run_simulation(steps=5, device_type="ventilator", fidelity="L2")
    print(f"L2 Snapshot sample: {sim_result_l2['snapshots'][-1]['values']['Pressure(cmH2O)']}")

    # 5. Test Fault Injection and Compliance Mitigation Suggestions
    print("\nTesting Fault Injection (Pressure Sensor Bias +20%)...")
    # REQ-VENT-004 is Barotrauma safety req with max_pressure=40
    fault_result = run_faulty_simulation(
        parameter="pressure",
        bias=0.2, # +20% bias
        steps=5,
        device_type="ventilator"
    )
    
    print("Running compliance gate on faulty simulation...")
    gate_report = validate_design()
    print(f"Overall Compliance: {gate_report['overall_status']}")
    
    for result in gate_report['results']:
        if result['standard'] == 'ISO 14971':
            for entry in result['details']:
                if entry['simulation_violations']:
                    print(f"\n[VIOLATION] Req: {entry['requirement_id']}")
                    print(f"Hazard: {entry['hazard']}")
                    print(f"Mitigation Suggestion: {entry['mitigation_suggestion']}")
                    
    if gate_report['overall_status'] != "FAIL":
        print("FAILED: Compliance gate should have failed due to fault")
        sys.exit(1)

    print("\nAdvanced Features Verification OK")

if __name__ == "__main__":
    test_advanced_features()
