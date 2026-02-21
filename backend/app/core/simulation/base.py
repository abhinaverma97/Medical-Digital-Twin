class SimulationState:
    """
    Holds the state of the system at a given timestep.
    """
    def __init__(self, time_step: int, values: dict):
        self.time_step = time_step
        self.values = values

    def snapshot(self):
        return {
            "t": self.time_step,
            "values": self.values
        }


class BaseDigitalTwin:
    """
    Base class for all device digital twins.
    """

    def __init__(self, fidelity: str = "L1"):
        self.fidelity = fidelity
        self.time = 0
        self.state_log = []

    def step(self):
        """
        Override in child classes.
        """
        raise NotImplementedError

    def log_state(self, values: dict):
        state = SimulationState(self.time, values)
        self.state_log.append(state)

    def run(self, steps: int = 1):
        for _ in range(steps):
            values = self.step()
            self.log_state(values)
            self.time += 1

        return [s.snapshot() for s in self.state_log]