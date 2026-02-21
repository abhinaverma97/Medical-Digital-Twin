class SimulationEngine:
    """
    Runs simulations on any digital twin.
    """

    def __init__(self, twin):
        self.twin = twin

    def run(self, steps=10):
        return self.twin.run(steps)