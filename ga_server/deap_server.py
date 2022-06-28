
from copy import deepcopy
import json
from typing import Any
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

    def run_one_gen(self):
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
            "settings": {
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
        }

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

    def info(ga_data: GADataDeap, _) -> str:
        return (json_enc.encode({
            "info": "all",
            "data": ga_data.info()
        }), False)

    def run_one_gen(ga_data: GADataDeap, _) -> str:
        gen_stats = ga_data.run_one_gen()
        return (json_enc.encode({
            "info": "one-gen",
            "data": {
                "generation": ga_data.generation,
                "gen_stats": gen_stats
            }
        }), True)

    default_data = GADataDeap(pop, toolbox, cxpb, mutpb, stats)
    server: GAServer[GADataDeap] = GAServer(
        host, port, lambda: deepcopy(default_data),
        commands = {
            "info": info,
            "run-one-gen": run_one_gen,
        },
        command_protocol = "generic"
    )

    server.run()
