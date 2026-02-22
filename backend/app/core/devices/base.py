from typing import List, Dict, Any

class MedicalDevice:
    device_name: str
    device_class: str

    def get_default_subsystems(self) -> List[str]:
        raise NotImplementedError

    def get_design_constraints(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_architecture(self) -> Dict[str, List[str]]:
        """Returns a hierarchical map of subsystems to components."""
        return {s: [] for s in self.get_default_subsystems()}

    def get_detailed_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns minute technical details for components.
        Format: { "ComponentName": {"type": "MCU", "model": "STM32H7", "bus": "CAN", ...} }
        """
        return {}

    def get_software_stack(self) -> List[Dict[str, str]]:
        """Returns software layers: HAL, OS, Middleware, Application."""
        return []

    def get_standard_safety_components(self) -> List[str]:
        """Returns standard safety components based on device class."""
        if self.device_class in ["Class II", "Class III"]:
            return ["Safety MCU", "Watchdog Timer", "Isolated Power Supply"]
        return []

    def get_default_interfaces(self) -> List[Dict[str, str]]:
        """Returns default interfaces between subsystems for visualization."""
        return []
