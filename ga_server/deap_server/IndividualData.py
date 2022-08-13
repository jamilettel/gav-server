
from copy import deepcopy


class IndividualData:
    id = 1


    def mate_decorator(func):
        def wrapper(*args, **kwargs):
            child1 = deepcopy(args[0])
            child2 = deepcopy(args[1])
            child1.visualization_data.set_parents(args[0].visualization_data.id, args[1].visualization_data.id)
            child2.visualization_data.set_parents(args[0].visualization_data.id, args[1].visualization_data.id)
            return func(child1, child2, **kwargs)
        return wrapper

    def mutate_decorator(func):
        def wrapper(*args, **kwargs):
            individual = deepcopy(args[0])
            individual.visualization_data.set_as_mutated()
            return func(individual, **kwargs)
        return wrapper


    def _set_new_id(self):
        self.id = IndividualData.id
        IndividualData.id += 1

    def __init__(self):
        self.id = IndividualData.id
        self.age = 0
        self.parent1_id: int | None = None
        self.parent2_id: int | None = None
        self.mutated = False
        IndividualData.id += 1

    def set_as_mutated(self):
        self._set_new_id()
        self.mutated = True
        self.age = 0
        self.parent1_id = None
        self.parent2_id = None

    def set_parents(self, parent1_id, parent2_id):
        self._set_new_id()
        self.age = 0
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id

    def __str__(self):
        return f"IND {self.id}: {self.age}"
