#!/usr/bin/env python
import json
import random
from typing import Dict
from deap import creator, base, tools, algorithms
import array

import numpy
from ga_server.deap_server.deap_server import DEAPServer
from ga_server.deap_server.ga_data_deap import GADataDeap
from ga_server.deap_server.deap_settings import DeapSetting
from ga_server.deap_server.deap_settings_presets import get_cxpb_deap_setting, get_mutpb_deap_setting
from ga_server.deap_server.individual_encoding import get_ind_enc_indexes


with open("tsp.json", "r") as tsp_data:
    tsp = json.load(tsp_data)

distance_map = tsp["DistanceMatrix"]
IND_SIZE = tsp["TourSize"]

def evalTSP(individual):
    distance = distance_map[individual[-1]][individual[0]]
    for gene1, gene2 in zip(individual[0:-1], individual[1:]):
        distance += distance_map[gene1][gene2]
    return distance,


def general_stats_provider(ga_data: GADataDeap) -> Dict:
    return {
        "Optimal distance": str(tsp["OptDistance"]),
        "Best found distance": str(ga_data.hof.items[0].fitness.values[0]) if len(ga_data.hof.items) > 0 else "N/A",
    }

def get_tournsize(ga_data: GADataDeap):
    return ga_data.additional_settings['tournsize']

def set_tournsize(ga_data: GADataDeap, tournsize: int):
    ga_data.additional_settings['tournsize'] = tournsize
    ga_data.toolbox.register(f"select_Tournament", tools.selTournament, tournsize=tournsize)
    if ga_data.select_value == 'Tournament':
        GADataDeap.upd_select(ga_data, ga_data.select_value)

def main():
    TOURNSIZE = 3

    server = DEAPServer(
        algorithm_kwargs={
            'cxpb': 0.7,
            'mutpb': 0.2,
            'ngen': 1,
            'verbose': False
        },
        additional_settings={
            'tournsize': TOURNSIZE,
        },
        algorithm=algorithms.eaSimple,
        title="Travelling Salesman Problem",
        initial_pop_size=300,
        stats=tools.Statistics(lambda ind: ind.fitness.values),
        general_stats_provider=general_stats_provider,
        settings=[
            get_mutpb_deap_setting(),
            get_cxpb_deap_setting(),
            DeapSetting(
                'number',
                'Tournament size',
                get_tournsize,
                set_tournsize,
                setting_range=[1, 300],
                min_increment=1
            )
        ],
        individual_encoding=get_ind_enc_indexes()
    )

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    DEAPServer.create("Individual", array.array, typecode='i', fitness=creator.FitnessMin)

    server.toolbox.register("indices", random.sample, range(IND_SIZE), IND_SIZE)

    server.toolbox.register("individual", tools.initIterate, creator.Individual, server.toolbox.indices)
    server.toolbox.register("population", tools.initRepeat, list, server.toolbox.individual)

    server.toolbox.register("evaluate", evalTSP)

    server.register_mate("Partially Matched", tools.cxPartialyMatched, default=True)
    server.register_mate("Ordered", tools.cxOrdered)

    server.register_mutate("Shuffle Indexes", tools.mutShuffleIndexes, default=True, indpb=0.05)
    
    server.register_select("Tournament", tools.selTournament, default=True, tournsize=TOURNSIZE)
    server.register_select("Best", tools.selBest)
    server.register_select("Random", tools.selRandom)
    server.register_select("Random2", tools.selRandom)
    server.register_select("Random3", tools.selRandom)
    server.register_select("Random4", tools.selRandom)
    server.register_select("Random5", tools.selRandom)
    server.register_select("Random6", tools.selRandom)

    server.stats.register("Trip distance", lambda x: {'Maximum': numpy.max(x), 'Minimum': numpy.min(x), 'Mean': numpy.mean(x)})
    server.stats.register("Standard deviation in trip distance", lambda x: {'Standard deviation': numpy.std(x)})
    server.stats.register("Standard deviation in trip distance 2", lambda x: {'std': numpy.std(x)})

    server.run()

if __name__ == "__main__":
    main()