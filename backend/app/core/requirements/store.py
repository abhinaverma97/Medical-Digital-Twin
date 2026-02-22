class RequirementStore:
    def __init__(self):
        self._requirements = {}

    def add(self, req):
        self._requirements[req.id] = req

    def get_all(self):
        return list(self._requirements.values())

    def get_by_subsystem(self, subsystem):
        return [
            r for r in self._requirements.values()
            if r.subsystem == subsystem
        ]

    def clear(self):
        self._requirements = {}