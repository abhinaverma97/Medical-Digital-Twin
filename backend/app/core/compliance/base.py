class ComplianceResult:
    def __init__(self, standard, status, details):
        self.standard = standard
        self.status = status  # PASS / FAIL
        self.details = details

    def to_dict(self):
        return {
            "standard": self.standard,
            "status": self.status,
            "details": self.details
        }