class MedicalDevice:
    device_name: str
    device_class: str

    def get_default_subsystems(self):
        raise NotImplementedError

    def get_design_constraints(self):
        raise NotImplementedError