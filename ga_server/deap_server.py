
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
                "cxpb": self.cxpb,
                "mutpb": self.mutpb,
            }
        }

def run_deap_server(
        pop,
        toolbox: base.Toolbox,
        cxpb: float,
        mutpb: float,
        stats: tools.Statistics,
        host: str = "localhost",
        port: int = 8080):

    json_enc = json.encoder.JSONEncoder()

    def info(client: GAClient[GADataDeap], _) -> str:
        return json_enc.encode(client.ga_data.info())

    def run_one_gen(client: GAClient[GADataDeap], _) -> str:
        gen_stats = client.ga_data.run_one_gen()
        return json_enc.encode({
            'generation': client.ga_data.generation,
            'gen_stats': gen_stats
        })

    default_data = GADataDeap(pop, toolbox, cxpb, mutpb, stats)
    server = GAServer(
        host, port, lambda: deepcopy(default_data),
        commands={
            "info": info,
            "run_one_gen": run_one_gen,
        }
    )



    server.run()


    # for _ in range(40):
    #     offspring = toolbox.select(pop, len(pop))
    #     offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)
    #     fitness = toolbox.map(toolbox.evaluate, offspring)
    #     for fit, ind in zip(fitness, offspring):
    #         ind.fitness.values = fit

    #     if hof is not None:
    #         hof.update(offspring)

    #     pop[:] = offspring
    #     if stats is not None:
    #         record = stats.compile(pop)
    #         print(record)
    # print(hof.items[0].__getattribute__())
