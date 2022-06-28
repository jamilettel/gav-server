
from copy import deepcopy
import json
from typing import Any, Tuple
from deap import base
from deap import tools
from deap import algorithms
from ga_server.client import GAClient

from ga_server.gas import GAServer

class GADataDeap:

    generation = 0
    records: list[dict[str, Any]] = []

    def __init__(
        self,
        pop,
        toolbox: base.Toolbox,
        cxpb: float,
        mutpb: float,
        stats: tools.Statistics,
        hof = tools.HallOfFame(1)
    ):
        self.pop = pop
        self.toolbox = toolbox
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.stats = stats
        self.hof = hof

    def run_one_gen(self) -> dict:
        offspring = self.toolbox.select(self.pop, len(self.pop))
        offspring = algorithms.varAnd(offspring, self.toolbox, self.cxpb, self.mutpb)
        fitness = self.toolbox.map(self.toolbox.evaluate, offspring)
        for fit, ind in zip(fitness, offspring):
            ind.fitness.values = fit

        self.hof.update(offspring)

        self.pop[:] = offspring

        record = self.stats.compile(self.pop)
        self.records.append(record)

        self.generation += 1
        return record

    def info(self) -> dict:
        return {
            "generation": self.generation,
            "all_stats": self.records,
            "settings": self.settings()
        }

    def settings(self) -> dict:
        return {
            "cxpb": {
                "type": "number",
                "value": self.cxpb,
                "range": [0.0, 1.0]
            },
            "mutpb": {
                "type": "number",
                "value": self.mutpb,
                "range": [0.0, 1.0]
            },
        }

    def set_settings(self, command: dict) -> bool:
        if "setting_name" not in command or "setting_value" not in command:
            return False
        setting_name = command["setting_name"]
        setting_value = command["setting_value"]
        match setting_name:
            case "cxpb":
                if type(setting_value) is float and setting_value >= 0.0 and setting_value <= 1.0:
                    self.cxpb = setting_value
                    return True
            case "mutpb":
                if type(setting_value) is float and setting_value >= 0.0 and setting_value <= 1.0:
                    self.mutpb = setting_value
                    return True
        return False

def run_deap_server(
    pop,
    toolbox: base.Toolbox,
    cxpb: float,
    mutpb: float,
    stats: tools.Statistics,
    host: str = "localhost",
    port: int = 8080
):
    json_enc = json.encoder.JSONEncoder()

    def info(ga_data: GADataDeap, _) -> Tuple[str, bool]:
        return (json_enc.encode({
            "info": "all",
            "data": ga_data.info()
        }), False)

    def run_one_gen(ga_data: GADataDeap, _) -> Tuple[str, bool]:
        gen_stats = ga_data.run_one_gen()
        return (json_enc.encode({
            "info": "one-gen",
            "data": {
                "generation": ga_data.generation,
                "gen_stats": gen_stats
            }
        }), True)

    def settings(ga_data: GADataDeap, _) -> Tuple[str, bool]:
        return (json_enc.encode({
            "info": "settings",
            "settings": ga_data.settings()
        }), False)

    def set_setting(ga_data: GADataDeap, command: dict) -> Tuple[str, bool] | None:
        update = ga_data.set_settings(command)
        if update:
            return (settings(ga_data, {})[0], True)
        return None

    default_data = GADataDeap(pop, toolbox, cxpb, mutpb, stats)
    server: GAServer[GADataDeap] = GAServer(
        host, port, lambda: deepcopy(default_data),
        commands = {
            "info": info,
            "run-one-gen": run_one_gen,
            "settings": settings,
            "set-setting": set_setting,
        },
        command_protocol = "generic"
    )

    server.run()