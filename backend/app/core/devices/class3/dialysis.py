from ..base import MedicalDevice

class DialysisMachine(MedicalDevice):
    device_name = "Hemodialysis Machine"
    device_class = "Class III"

    def get_default_subsystems(self):
        return [
            "Blood Circuit",
            "Dialysate Circuit",
            "Extracorporeal Module",
            "Ultrafiltration Control",
            "Safety/Alarm System",
            "Power"
        ]

    def get_design_constraints(self):
        return {
            "blood_flow_range": (50, 600), # mL/min
            "dialysate_flow_range": (300, 800), # mL/min
            "max_venous_pressure": 200, # mmHg
            "max_transmembrane_pressure": 500 # mmHg
        }
