class ECS:
    def __init__(self):
        self.next_id = 1
        self.components = {}

    def create_entity(self):
        eid = self.next_id
        self.next_id += 1
        return eid

    def add_component(self, entity, component):
        self.components.setdefault(type(component), {})[entity] = component

    def get(self, comp_type, entity):
        return self.components.get(comp_type, {}).get(entity)

    def get_entities_with(self, *comp_types):
        if not comp_types:
            return []
        sets = [set(self.components.get(c, {})) for c in comp_types]
        return set.intersection(*sets)
