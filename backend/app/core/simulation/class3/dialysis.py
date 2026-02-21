from ..base import BaseDigitalTwin

class DialysisTwin(BaseDigitalTwin):
    """
    Digital Twin for Class III Hemodialysis Machine.
    Models Blood Flow, Dialysate Flow, and TMP (Transmembrane Pressure).
    """

    def __init__(
        self,
        target_bfr: float = 300.0,  # Blood Flow Rate (mL/min)
        target_dfr: float = 500.0,  # Dialysate Flow Rate (mL/min)
        max_tmp:    float = 500.0,  # Transmembrane Pressure (mmHg)
        fidelity: str = "L2"
    ):
        super().__init__(fidelity)
        self.target_bfr = target_bfr
        self.target_dfr = target_dfr
        self.max_tmp    = max_tmp

        # State
        self.blood_flow_rate     = 0.0
        self.dialysate_flow_rate = 0.0
        self.tmp                 = 0.0 # Transmembrane Pressure
        self.urea_clearance      = 0.0

        # Safety flags
        self.tmp_high_alarm = False

    def step(self) -> dict:
        # P-control approximation for flow tracking
        self.blood_flow_rate += 0.2 * (self.target_bfr - self.blood_flow_rate)
        self.dialysate_flow_rate += 0.2 * (self.target_dfr - self.dialysate_flow_rate)

        if self.fidelity == "L3":
            # Higher fidelity model for TMP
            # TMP is roughly proportional to flow and membrane resistance
            resistance = 1.2
            self.tmp = (self.blood_flow_rate * 0.5 + self.dialysate_flow_rate * 0.2) * resistance
        else:
            self.tmp = (self.blood_flow_rate * 0.1) + (self.dialysate_flow_rate * 0.05)

        # Urea clearance estimation (K = (BFR * DFR) / (BFR + DFR) simplified)
        self.urea_clearance = (self.blood_flow_rate * self.dialysate_flow_rate) / (self.blood_flow_rate + self.dialysate_flow_rate + 0.1)

        self.tmp_high_alarm = self.tmp > self.max_tmp

        return {
            "BloodFlowRate(mL/min)": round(self.blood_flow_rate, 1),
            "DialysateFlowRate(mL/min)": round(self.dialysate_flow_rate, 1),
            "TMP(mmHg)": round(self.tmp, 1),
            "UreaClearance(mL/min)": round(self.urea_clearance, 1),
            "TMPHighAlarm": self.tmp_high_alarm,
            "TargetBFR": self.target_bfr,
        }
