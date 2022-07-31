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
        cxpb: float,
        mutpb: float,
        stats: tools.Statistics,
        mate_settings: List[str],
        mutate_settings: List[str],
        select_settings: List[str],
        mate_default: str,
        mutate_default: str,
        select_default: str,
        hof = tools.HallOfFame(1),
    ):
        self.pop = pop
        self.toolbox = toolbox
        self.cxpb = cxpb
        self.mutpb = mutpb
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

    ### Actions

    def run_one_gen(self) -> dict:
        algorithms.eaSimple(self.pop, self.toolbox, self.cxpb, self.mutpb, 1, halloffame=self.hof, verbose=False)

        record = self.stats.compile(self.pop)
        self.records.append(record)

        self.generation += 1
        return record

    ### Information

    def info(self) -> dict:
        popdata = [{ 
            'chromosome': ind.tolist(),
            'fitness': ind.fitness.values[0] if len(ind.fitness.values) > 0 else None
        } for ind in self.pop]

        return {
            "all_stats": self.records,
            "population": popdata,
            "settings": self.settings()
        }

    def settings(self) -> dict:
        settings = {
            SETTING_KEYS["cxpb"]["name"]: {
                "type": "number",
                "value": self.cxpb,
                "range": [0.0, 1.0],
                "min_increment": 0.1,
            },
            SETTING_KEYS["mutpb"]["name"]: {
                "type": "number",
                "value": self.mutpb,
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
            self.cxpb = setting_value
            return True
        return False

    def upd_mutpb(self, setting_value) -> bool:
        if isnum(setting_value) and setting_value >= 0.0 and setting_value <= 1.0:
            self.mutpb = setting_value
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

