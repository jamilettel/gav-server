from deap import algorithms, base, tools
from typing import Any, List

SETTING_KEYS = {
    "mutpb": {
        "name": "Mutation probability",
        "handler": lambda ga_data, command: ga_data.upd_mutpb(command)
    },
    "cxpb": {
        "name": "Crossover probability",
        "handler": lambda ga_data, command: ga_data.upd_cxpb(command)
    },
    "mate": {
        "name": "Crossover",
        "handler": lambda ga_data, command: ga_data.upd_mate(command)
    },
    "mutate": {
        "name": "Mutation",
        "handler": lambda ga_data, command: ga_data.upd_mutate(command)
    },
    "select": {
        "name": "Selection",
        "handler": lambda ga_data, command: ga_data.upd_select(command)
    },
}

def isnum(var):
    return type(var) is float or type(var) is int

class GADataDeap:

    def __init__(
        self,
        pop,
        toolbox: base.Toolbox,
        algorithm_kwargs: dict,
        stats: tools.Statistics,
        mate_settings: List[str],
        mutate_settings: List[str],
        select_settings: List[str],
        mate_default: str,
        mutate_default: str,
        select_default: str,
        hof: tools.HallOfFame,
        algorithm = algorithms.eaSimple,
    ):
        self.pop = pop
        self.toolbox = toolbox
        self.algorithm_kwargs = algorithm_kwargs
        self.stats = stats
        self.hof = hof
        self.generation = 0
        self.records: list[dict[str, Any]] = []
        self.mate_settings = mate_settings
        self.mutate_settings = mutate_settings
        self.select_settings = select_settings
        self.mate_value = mate_default
        self.mutate_value = mutate_default
        self.select_value = select_default
        self.algorithm = algorithm


    ### Utils

    def get_pop_data(self) -> List[dict]:
        return [{ 
            'Chromosome': ind.tolist(),
            'Fitness': ind.fitness.values[0] if len(ind.fitness.values) > 0 else None
        } for ind in self.pop]

    ### Actions

    def run_one_gen(self) -> dict:
        self.algorithm(self.pop, self.toolbox, **self.algorithm_kwargs, ngen=1, halloffame=self.hof, verbose=False)

        record = self.stats.compile(self.pop)
        self.records.append(record)

        self.generation += 1
        return record

    ### Information

    def info(self) -> dict:
        popdata = self.get_pop_data()

        return {
            "all_stats": self.records,
            "population": popdata,
            "settings": self.settings()
        }

    def settings(self) -> dict:
        settings = {
            SETTING_KEYS["cxpb"]["name"]: {
                "type": "number",
                "value": self.algorithm_kwargs['cxpb'],
                "range": [0.0, 1.0],
                "min_increment": 0.1,
            },
            SETTING_KEYS["mutpb"]["name"]: {
                "type": "number",
                "value": self.algorithm_kwargs['mutpb'],
                "range": [0.0, 1.0],
                "min_increment": 0.1,
            },
        }
        if len(self.mate_settings) > 1:
            settings[SETTING_KEYS["mate"]["name"]] = {
                "type": "string",
                "value": self.mate_value,
                "values": self.mate_settings
            }
        if len(self.mutate_settings) > 1:
            settings[SETTING_KEYS["mutate"]["name"]] = {
                "type": "string",
                "value": self.mutate_value,
                "values": self.mutate_settings
            }
        if len(self.select_settings) > 1:
            settings[SETTING_KEYS["select"]["name"]] = {
                "type": "string",
                "value": self.select_value,
                "values": self.select_settings
            }
        return settings


    ### Settings

    def upd_cxpb(self, setting_value) -> bool:
        if isnum(setting_value) and setting_value >= 0.0 and setting_value <= 1.0:
            self.algorithm_kwargs['cxpb'] = setting_value
            return True
        return False

    def upd_mutpb(self, setting_value) -> bool:
        if isnum(setting_value) and setting_value >= 0.0 and setting_value <= 1.0:
            self.algorithm_kwargs['mutpb'] = setting_value
            return True
        return False

    def upd_mate(self, setting_value) -> bool:
        if type(setting_value) is not str or setting_value not in self.mate_settings:
            return False
        self.mate_value = setting_value
        self.toolbox.register("mate", getattr(self.toolbox, f"mate_{setting_value}"))
        return True

    def upd_mutate(self, setting_value) -> bool:
        if type(setting_value) is not str or setting_value not in self.mutate_settings:
            return False
        self.mutate_value = setting_value
        self.toolbox.register("mutate", getattr(self.toolbox, f"mutate_{setting_value}"))
        return True

    def upd_select(self, setting_value) -> bool:
        if type(setting_value) is not str or setting_value not in self.select_settings:
            return False
        self.select_value = setting_value
        self.toolbox.register("select", getattr(self.toolbox, f"select_{setting_value}"))
        return True

    ### Settings handler
    
    def set_settings(self, command: dict) -> bool:
        if "setting_name" not in command or "setting_value" not in command:
            return False
        setting_name = command["setting_name"]
        setting_value = command["setting_value"]
        if type(setting_name) is not str:
            return False
        for setting in SETTING_KEYS:
            if SETTING_KEYS[setting]["name"] == setting_name:
                return SETTING_KEYS[setting]["handler"](self, setting_value)
        return False

