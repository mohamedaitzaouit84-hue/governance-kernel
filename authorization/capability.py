"""authorization/capability.py — نموذج الصلاحيات."""


class Capability:
    def __init__(self, name, resource, actions):
        self.name = name
        self.resource = resource
        self.actions = set(actions)

    def allows(self, action):
        return action in self.actions or "*" in self.actions

    def to_dict(self):
        return {"name": self.name, "resource": self.resource,
                "actions": sorted(self.actions)}
