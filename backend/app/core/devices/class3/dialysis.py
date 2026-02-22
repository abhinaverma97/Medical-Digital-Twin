from ..base import MedicalDevice

class DialysisMachine(MedicalDevice):
    device_name = "Hemodialysis Machine"
    device_class = "Class III"

    def get_default_subsystems(self):
        return [
            "Blood Circuit", "Dialysate Circuit", "Ultrafiltration", 
            "Extracorporeal Safety", "Control System", "Power & Thermal"
        ]

    def get_architecture(self):
        return {
            "Blood Circuit": ["Arterial Peristaltic Pump", "Venous Clamp", "Heparin Infusion Pump"],
            "Dialysate Circuit": ["Dialysate Heater", "Degassing Module", "Conductivity Probe"],
            "Ultrafiltration": ["UF Volumetric Balancing Chamber", "UF Discard Pump"],
            "Extracorporeal Safety": ["Ultrasonic Bubble Detector", "Optical Blood Leak Detector", "Venous Pressure Transducer"],
            "Control System": ["Master Controller (STM32H7)", "Protection Controller (STM32F4)", "UI Processor (IMX8)"],
            "Power & Thermal": ["Isolation Transformer", "UPS Battery Module", "Heater Control SSR"]
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
            "Protection Controller (STM32F4)": {
                "type": "Safety MCU",
                "model": "STM32F429",
                "purpose": "Safety logic and independent shutdown"
            },
            "Ultrasonic Bubble Detector": {
                "type": "Critical Sensor",
                "resolution": "5uL bubble",
                "interface": "Analog/Frequency"
            },
            "Arterial Peristaltic Pump": {
                "type": "Actuator",
                "motor": "Brushless DC",
                "encoder": "4096 PPR",
                "comms": "CAN"
            }
        }

    def get_software_stack(self):
        return [
            {"layer": "Drivers", "name": "STM32 Cube HAL & LL"},
            {"layer": "OS", "name": "Azure RTOS (ThreadX) - IEC 62304 Class C"},
            {"layer": "Safety", "name": "STL (Self-Test Library)"},
            {"layer": "Application", "name": "Dialysis Therapy Manager"}
        ]

    def get_design_constraints(self):
        return {
            "blood_flow_range": (50, 600),
            "dialysate_flow_range": (300, 800),
            "max_venous_pressure": 300,
            "safety_shutdown_time_ms": 50
        }

    def get_default_interfaces(self):
        return [
            {"source": "Control System", "target": "Blood Circuit", "signal": "Pump Speed Control"},
            {"source": "Control System", "target": "Dialysate Circuit", "signal": "Temperature/Flow Control"},
            {"source": "Extracorporeal Safety", "target": "Control System", "signal": "Bubble/Leak Detection"},
            {"source": "Power & Thermal", "target": "Control System", "signal": "System Status"},
            {"source": "Ultrafiltration", "target": "Control System", "signal": "UF Balancing Telemetry"}
        ]

