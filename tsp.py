#!/usr/bin/env python
#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import array
from os import getpid
import random
import json
from typing import Dict

import numpy

from ga_server.deap_server import run_deap_server

from deap import base
from deap import creator
from deap import tools

# gr*.json contains the distance map in list of list style in JSON format
# Optimal solutions are : gr17 = 2085, gr24 = 1272, gr120 = 6942
with open("tsp.json", "r") as tsp_data:
    tsp = json.load(tsp_data)

distance_map = tsp["DistanceMatrix"]
IND_SIZE = tsp["TourSize"]

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='i', fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("indices", random.sample, range(IND_SIZE), IND_SIZE)

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalTSP(individual):
    distance = distance_map[individual[-1]][individual[0]]
    for gene1, gene2 in zip(individual[0:-1], individual[1:]):
        distance += distance_map[gene1][gene2]
    return distance,

toolbox.register("mate", tools.cxPartialyMatched)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evalTSP)

def general_stats_provider(pop, _toolbox: base.Toolbox, hof: tools.HallOfFame | None) -> Dict:
    general_stats = {}
    general_stats["Optimal distance"] = str(tsp["OptDistance"])
    if hof != None and len(hof.items) > 0:
        general_stats["Best distance"] = str(hof.items[0].fitness.values[0])
    general_stats["Population"] = str(len(pop))
    return general_stats

def main():
    random.seed(getpid())

    pop = toolbox.population(n=300)

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Trip distance", lambda x: {'max': numpy.max(x), 'min': numpy.min(x), 'mean': numpy.mean(x)})
    stats.register("Standard deviation in trip distance", lambda x: {'std': numpy.std(x)})

    run_deap_server(
        pop, 
        toolbox, 
        cxpb=0.7, 
        mutpb=0.2,
        stats=stats,
        title="Travelling Salesman Problem",
        hof=hof,
        general_stats_provider=general_stats_provider
    )

    if len(hof.items) != 0:
        print(f'Best distance found: {hof.items[0].fitness.values[0]}')
        print(f'Optimal distance {tsp["OptDistance"]}')
    return pop, stats, hof

if __name__ == "__main__":
    main()
