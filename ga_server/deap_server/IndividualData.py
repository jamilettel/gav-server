
from copy import deepcopy


class IndividualData:
    id = 1

    def mate_decorator(func):
        def wrapper(*args, **kwargs):
            child1, child2 = func(deepcopy(args[0]), deepcopy(args[1]), **kwargs)
            child1.visualization_data.set_parents(args[0].visualization_data.id, args[1].visualization_data.id)
            child2.visualization_data.set_parents(args[0].visualization_data.id, args[1].visualization_data.id)
            return child1, child2
        return wrapper

    def mutate_decorator(func):
        def wrapper(*args, **kwargs):
            individual, = func(deepcopy(args[0]), **kwargs)
            individual.visualization_data.set_as_mutated(args[0].visualization_data.id)
            return individual,
        return wrapper


    def _set_new_id(self):
        self.id = IndividualData.id
        IndividualData.id += 1

    def __init__(self):
        self._set_new_id()
        self.age = -1
        self.parent1_id: int = -1
        self.parent2_id: int = -1
        self.mutated_from = -1

    def set_as_mutated(self, mutated_from: int):
        self._set_new_id()
        self.mutated_from = mutated_from
        self.age = 0
        self.parent1_id = -1
        self.parent2_id = -1

    def set_parents(self, parent1_id, parent2_id):
        self._set_new_id()
        self.mutated_from = -1
        self.age = 0
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'age': self.age,
            'mutated_from': self.mutated_from,
            'parent1_id': self.parent1_id,
            'parent2_id': self.parent2_id,
        }
