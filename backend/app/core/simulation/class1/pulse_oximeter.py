from ..base import BaseDigitalTwin


class PulseOximeterTwin(BaseDigitalTwin):
    """
    Digital Twin for Class I Pulse Oximeter — L2 requirement-driven model.
    
    Dynamically tracks SpO2 and Pulse Rate toward target values.
    Triggers alarms if safety limits (derived from requirements) are breached.
    """
    _KP = 0.1  # tracking gain for smooth transitions

    def __init__(
        self,
        target_spo2: float = 98.0,
        min_spo2:    float = 90.0,
        target_hr:   float = 70.0,
        max_hr:      float = 120.0,
        fidelity: str = "L2"
    ):
        super().__init__(fidelity)
        self.target_spo2 = target_spo2
        self.min_spo2    = min_spo2
        self.target_hr   = target_hr
        self.max_hr      = max_hr

        # Internal State
        self.spo2 = 95.0  # initial value
        self.hr   = 60.0  # initial value

        # Alarm flags
        self.spo2_low_alarm = False
        self.hr_high_alarm  = False

    def step(self) -> dict:
        """
        One simulation tick.
        Updates SpO2 and Pulse Rate using a simple proportional tracking model.
        """
        # Update metrics
        self.spo2 += self._KP * (self.target_spo2 - self.spo2)
        self.hr   += self._KP * (self.target_hr - self.hr)

        # Evaluate safety constraints
        self.spo2_low_alarm = self.spo2 < self.min_spo2
        self.hr_high_alarm  = self.hr > self.max_hr

        return {
            "SpO2(%)":             round(self.spo2, 1),
            "PulseRate(bpm)":      round(self.hr, 1),
            "SpO2LowAlarm":        self.spo2_low_alarm,
            "PulseRateHighAlarm":  self.hr_high_alarm,
            "TargetSpO2(%)":       self.target_spo2,
            "TargetPulseRate":     self.target_hr
        }

    def set_target_spo2(self, value: float):
        self.target_spo2 = value

    def set_target_pulse_rate(self, value: float):
        self.target_hr = value