import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.requirements.schema import Requirement
from backend.app.api.requirements import store
from backend.app.api.design import build_design

def test_minimal():
    store.clear()
    r_dict = {
        "id": "REQ-DIAL-001",
        "title": "BFR",
        "description": "Desc",
        "type": "functional",
        "subsystem": "Blood Circuit",
        "parameter": "Flow",
        "verification": {"method": "simulation", "description": "Verify"}
    }
    r = Requirement(**r_dict)
    store.add(r)
    
    print(f"Added: {r.id}")
    design = build_design(device_type="dialysis")
    print(f"Device: {design['device']}")
    print(f"Subsystems: {design['subsystems']}")
    print("SUCCESS")

if __name__ == "__main__":
    test_minimal()
