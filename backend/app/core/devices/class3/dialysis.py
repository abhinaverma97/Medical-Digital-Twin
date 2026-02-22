from ..base import MedicalDevice

class DialysisMachine(MedicalDevice):
    device_name = "Hemodialysis Machine Digital Twin"
    device_class = "Class III"

    def get_default_subsystems(self):
        return [
            "BloodCircuit", 
            "DialysateCircuit", 
            "Ultrafiltration", 
            "ExtracorporealSafety", 
            "ControlSystem", 
            "PowerAndThermal",
            "Display&UI"
        ]

    def get_architecture(self):
        return {
            "BloodCircuit": [
                {"name": "Arterial Peristaltic Pump", "category": "Hardware (Mechanical)"},
                {"name": "Venous Clamp", "category": "Hardware (Mechanical)"},
                {"name": "Heparin Infusion Pump", "category": "Hardware (Mechanical)"},
                {"name": "Extracorporeal Tubing Set", "category": "Enclosure Packaging"},
                {"name": "Blood Pump Control Logic", "category": "Embedded Software"}
            ],
            "DialysateCircuit": [
                {"name": "Dialysate Heater Config", "category": "Hardware (Electronic)"},
                {"name": "Degassing Module", "category": "Hardware (Mechanical)"},
                {"name": "Conductivity Probe", "category": "Hardware (Electronic)"},
                {"name": "Dialysate Mixing Loop", "category": "Embedded Software"}
            ],
            "Ultrafiltration": [
                {"name": "UF Volumetric Chamber", "category": "Hardware (Mechanical)"},
                {"name": "UF Discard Pump", "category": "Hardware (Mechanical)"},
                {"name": "Fluid Mass Balance Algo", "category": "Application Software"}
            ],
            "ExtracorporealSafety": [
                {"name": "Ultrasonic Bubble Detector", "category": "Hardware (Electronic)"},
                {"name": "Optical Blood Leak Detector", "category": "Hardware (Electronic)"},
                {"name": "Venous Pressure Transducer", "category": "Hardware (Electronic)"},
                {"name": "Safety Protection MCU (STM32F4)", "category": "Hardware (Electronic)"},
                {"name": "ISO 60601-2-16 Trip Logic", "category": "Embedded Software"}
            ],
            "ControlSystem": [
                {"name": "Master Controller (STM32H7)", "category": "Hardware (Electronic)"},
                {"name": "Dual CAN-FD Bus", "category": "Hardware (Electronic)"},
                {"name": "Azure RTOS (ThreadX)", "category": "Embedded Software"},
                {"name": "Dialysis Therapy Manager", "category": "Application Software"}
            ],
            "PowerAndThermal": [
                {"name": "Medical Isolation XFMR", "category": "Hardware (Electronic)"},
                {"name": "UPS Battery Module", "category": "Hardware (Electronic)"},
                {"name": "Heater Control SSR", "category": "Hardware (Electronic)"},
                {"name": "Thermal Management Algo", "category": "Application Software"}
            ],
            "Display&UI": [
                {"name": "12-inch Capacitive Touch", "category": "Hardware (Electronic)"},
                {"name": "Splash-proof Bezel", "category": "Enclosure Packaging"},
                {"name": "Therapy GUI Software", "category": "Application Software"}
            ]
        }

    def get_detailed_components(self):
        return {
            "Master Controller (STM32H7)": {
                "type": "MCU",
                "model": "STM32H743IIT6",
                "clock": "480MHz",
                "bus": "Dual CAN-FD",
                "redundancy": "Lock-step capability"
            },
            "Safety Protection MCU (STM32F4)": {
                "type": "Safety MCU",
                "model": "STM32F429",
                "purpose": "Safety logic and independent shutdown"
            },
            "Ultrasonic Bubble Detector": {
                "type": "Critical Sensor",
                "resolution": "5uL bubble",
                "interface": "Analog/Frequency",
                "standard": "ISO 60601-2-16"
            },
            "Arterial Peristaltic Pump": {
                "type": "Actuator",
                "motor": "Brushless DC",
                "encoder": "4096 PPR",
                "comms": "CAN"
            },
            "Medical Isolation XFMR": {
                "type": "Safety Hardware",
                "rating": "5kV RMS Isolation",
                "leakage": "< 50uA"
            }
        }

    def get_software_stack(self):
        return []

    def get_design_constraints(self):
        return {
            "blood_flow_range": (50, 600),
            "dialysate_flow_range": (300, 800),
            "max_venous_pressure": 300,
            "safety_shutdown_time_ms": 50
        }

    def get_default_interfaces(self):
        return [
            {"source": "ControlSystem", "target": "BloodCircuit", "signal": "Pump Speed Control (CAN)"},
            {"source": "ControlSystem", "target": "DialysateCircuit", "signal": "Temperature/Flow Control"},
            {"source": "ExtracorporealSafety", "target": "ControlSystem", "signal": "Bubble/Leak Detection"},
            {"source": "PowerAndThermal", "target": "ControlSystem", "signal": "System Power & Status"},
            {"source": "Ultrafiltration", "target": "ControlSystem", "signal": "UF Balancing Telemetry"},
            {"source": "ControlSystem", "target": "Display&UI", "signal": "Therapy UI Data"}
        ]
