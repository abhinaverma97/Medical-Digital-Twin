from ..base import MedicalDevice

class Ventilator(MedicalDevice):
    device_name = "Ventilator"
    device_class = "Class II"

    def get_default_subsystems(self):
        return ["Airflow", "Control", "Sensing", "Alarms", "Power", "Connectivity"]

    def get_architecture(self):
        return {
            "Airflow": ["Blower Turbine", "O2 Proportional Valve", "Expiratory PEEP Valve"],
            "Control": ["Main Controller (ESP32-S3)", "Safety Co-processor", "Touch Display Interface"],
            "Sensing": ["Inspiratory Flow Sensor", "Proximal Pressure Sensor", "FiO2 Galvanic Cell"],
            "Alarms": ["Multi-tone Piezo", "Red/Yellow LED Matrix", "Silence Button"],
            "Power": ["Universal AC/DC (Medical Grade)", "Li-ion Battery Pack", "Charging Circuitry"],
            "Connectivity": ["WiFi/BLE Module", "Nurse Call Interface (Dry Contact)"]
        }

    def get_detailed_components(self):
        return {
            "Main Controller (ESP32-S3)": {
                "type": "MCU",
                "model": "ESP32-S3-WROOM-1",
                "bus": "SPI/I2C/UART",
                "purpose": "Main UI and Control Loop"
            },
            "Safety Co-processor": {
                "type": "Safety MCU",
                "model": "ATTiny1616",
                "bus": "UART (Isolated)",
                "purpose": "Independent Watchdog and Alarm monitor"
            },
            "Blower Turbine": {
                "type": "Actuator",
                "model": "Micronel U65",
                "control": "PWM (25kHz)",
                "speed": "60,000 RPM"
            },
            "Inspiratory Flow Sensor": {
                "type": "Sensor",
                "model": "Sensirion SFM3019",
                "interface": "I2C",
                "accuracy": "3% m.v."
            }
        }

    def get_software_stack(self):
        return [
            {"layer": "Drivers", "name": "Espressif HAL"},
            {"layer": "OS", "name": "FreeRTOS (Symmetric Multiprocessing)"},
            {"layer": "Middleware", "name": "LVGL (Graphics Library)"},
            {"layer": "Application", "name": "Lung Model Control Engine"}
        ]

    def get_design_constraints(self):
        return {
            "flow_rate_range": (5, 120),
            "max_pressure": 60,
            "latency_ms": 10
        }

    def get_default_interfaces(self):
        return [
            {"source": "Control", "target": "Airflow", "signal": "Blower PWM"},
            {"source": "Sensing", "target": "Control", "signal": "Pressure/Flow Telemetry"},
            {"source": "Power", "target": "Control", "signal": "System Power"},
            {"source": "Control", "target": "Alarms", "signal": "Alarm Trigger"}
        ]
