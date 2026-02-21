from ..base import MedicalDevice

class Ventilator(MedicalDevice):
    device_name = "Ventilator"
    device_class = "Class II"

    def get_default_subsystems(self):
        return [
            "Airflow",
            "Control",
            "Sensing",
            "Alarms",
            "Power"
        ]

    def get_design_constraints(self):
        return {
            "flow_rate_range": (5, 60),
            "max_pressure": 40
        }