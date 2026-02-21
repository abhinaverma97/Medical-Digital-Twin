class FaultInjector:
    """
    Injects faults into a digital twin at runtime.
    """

    def __init__(self, twin):
        self.twin = twin

    def apply_sensor_bias(self, parameter: str, bias: float):
        """
        Adds bias to a sensor value.
        Example: +0.1 means +10%
        """
        if hasattr(self.twin, parameter):
            original = getattr(self.twin, parameter)
            setattr(self.twin, parameter, original * (1 + bias))
        else:
            raise ValueError(f"Parameter {parameter} not found in twin")