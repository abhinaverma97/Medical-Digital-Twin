from ..base import MedicalDevice

class PulseOximeter(MedicalDevice):
    device_name = "Pulse Oximeter"
    device_class = "Class I"

    def get_default_subsystems(self):
        return [
            "Optical Sensing",
            "Signal Processing",
            "Display",
            "Power"
        ]

    def get_design_constraints(self):
        return {
            "spo2_range": (70, 100),
            "response_time_ms": 1000
        }