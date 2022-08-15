#!/usr/bin/env python
# For information about the kursawe benchmark, check out the doc linked below
# https://deap.readthedocs.io/en/master/api/benchmarks.html#deap.benchmarks.kursawe

import array
import logging
from ga_server.deap_server.deap_server import DEAPServer
import random

import numpy

from deap import algorithms
from deap import base
from deap import benchmarks
from deap import creator
from deap import tools

from ga_server.deap_server.deap_settings_presets import get_cxpb_deap_setting, get_lambda_deap_settings, get_mu_deap_settings, get_mutpb_deap_setting
from ga_server.deap_server.individual_encoding import get_ind_enc_range

def checkBounds(min, max):
    def decorator(func):
        def wrappper(*args, **kargs):
            offspring = func(*args, **kargs)
            for child in offspring:
                for i in range(len(child)):
                    if child[i] > max:
                        child[i] = max
                    elif child[i] < min:
                        child[i] = min
            return offspring
        return wrappper
    return decorator

def get_result_one_function(fitness_values, index, fct):
    values = [v.values[index] for v in fitness_values]
    return fct(values)

def get_result_fitness(fitness_values, fct):
    values = [sum(v.wvalues) for v in fitness_values]
    return fct(values)

def main():
    random.seed(64)
    MU, LAMBDA = 50, 100

    server = DEAPServer(
        port=8081,

        algorithm_kwargs={
            'mu': MU,
            'lambda_': LAMBDA,
            'cxpb': 0.5,
            'mutpb': 0.2,
            'ngen': 1,
            'verbose': False
        },
        algorithm=algorithms.eaMuPlusLambda,
        title="Kursawe Benchmark",
        initial_pop_size=MU,
        stats=tools.Statistics(lambda ind: ind.fitness),
        settings=[
            get_mutpb_deap_setting(),
            get_cxpb_deap_setting(),
            get_lambda_deap_settings(),
            get_mu_deap_settings(),
        ],
        individual_encoding=get_ind_enc_range(-5, 5)
    )

    creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
    DEAPServer.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)

    # Attribute generator
    server.toolbox.register("attr_float", random.uniform, -5, 5)

    # Structure initializers
    server.toolbox.register("individual", tools.initRepeat, creator.Individual, server.toolbox.attr_float, 3)
    server.toolbox.register("population", tools.initRepeat, list, server.toolbox.individual)


    server.toolbox.register("evaluate", benchmarks.kursawe)
    server.register_mate("cxBlend", tools.cxBlend, default=True, alpha=1.5)
    server.register_mutate("mutGaussian", tools.mutGaussian, default=True, mu=0, sigma=3, indpb=0.3)
    server.register_select("selNSGA2", tools.selNSGA2, default=True)

    server.decorate("mate", checkBounds(-5, 5))
    server.decorate("mutate", checkBounds(-5, 5)) 


    server.stats = tools.Statistics(lambda ind: ind.fitness)
    server.stats.register("Function 1", lambda values: {
        'mean': get_result_one_function(values, 0, numpy.mean),
        'min': get_result_one_function(values, 0, numpy.min),
        'max': get_result_one_function(values, 0, numpy.max),
    })
    server.stats.register("Function 2", lambda values: {
        'mean': get_result_one_function(values, 1, numpy.mean),
        'min': get_result_one_function(values, 1, numpy.min),
        'max': get_result_one_function(values, 1, numpy.max),
    })
    server.stats.register("Fitness", lambda values: {
        'mean': get_result_fitness(values, numpy.mean),
        'min': get_result_fitness(values, numpy.min),
        'max': get_result_fitness(values, numpy.max),
    })
    server.stats.register("Fitness Standard Deviation", lambda values: {
        'Standard deviation': get_result_fitness(values, numpy.std)
    })

    server.run()

if __name__ == "__main__":
    main()

    # import matplotlib.pyplot as plt
    # import numpy
    # 
    # front = numpy.array([ind.fitness.values for ind in pop])
    # plt.scatter(front[:,0], front[:,1], c="b")
    # plt.axis("tight")
    # plt.show()