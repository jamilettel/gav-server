
from deap import base
from deap import tools
from deap import algorithms


def start_deap_server(
        pop,
        toolbox: base.Toolbox,
        cxpb: float,
        mutpb: float,
        ngen: int,
        stats: tools.Statistics = None,
        hof: tools.HallOfFame = None):
    for _ in range(ngen):
        offspring = toolbox.select(pop, len(pop))
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)
        fitness = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fitness, offspring):
            ind.fitness.values = fit

        if hof is not None:
            hof.update(offspring)

        pop[:] = offspring
        if stats is not None:
            record = stats.compile(pop)
            print(record)
    print(hof.items[0].__getattribute__())
