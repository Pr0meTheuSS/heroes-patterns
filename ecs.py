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

    def remove_component(self, entity, comp_type):
        """Удаляет компонент указанного типа у сущности."""
        if comp_type in self.components and entity in self.components[comp_type]:
            del self.components[comp_type][entity]

    def delete_entity(self, entity):
        """Удаляет все компоненты сущности, по сути удаляя саму сущность."""
        for comp_dict in self.components.values():
            comp_dict.pop(entity, None) 
   
    def get(self, comp_type, entity):
        return self.components.get(comp_type, {}).get(entity)

    def get_entities_with(self, *comp_types):
        if not comp_types:
            return []
        sets = [set(self.components.get(c, {})) for c in comp_types]
        return set.intersection(*sets)

    def has(self, comp_type, entity):
        return entity in self.components.get(comp_type, {})
