# Genetic Algorithm Visualizer Server

This server is used to compute and send information about a genetic algorithm. 
An example of a client that can use this server can be found
[here](https://www.github.com/jamilettel/gav-client).

## Starting the server

To install dependencies and start the server, you can use the following commands:

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
./tsp.py
./kursawefct.py
```

[`tsp.py` ](./tsp.py) and [`kursawefct.py`](./kursawefct.py) are examples of how to setup and use the server when working respectively with the Travelling Salesman Problem, and the Kursawe Benchmark.

## Documentation about the protocol used

All communication is done with a websocket connection following a specific protocol that you can find [here](./Protocol/GENERAL_PROTOCOL.md).
This describes the general protocol that is used which can support many "sub protocols". This "sub protocol" is used to manipulate and read the data from the server. 

The sub protocol used in this server is [Generic Protocol](./Protocol/GENERIC_PROTOCOL.md), which is able to accomodate many basic scenarios.

## Implementation with DEAP

DEAP is a evolutionary computation framework. It allows its users to easily and quickly develop evolutionary algorithms. For the purposes of this project, we are only interested in the genetic algorithms aspect of DEAP.

### Encapsulation of DEAP

In order to make the server work, we need to manipulate the classes and read the data. This is done by encapsulating the different objects that are used when interacting with the DEAP framework.

### How to use the DEAPServer class

Here is a list of all the steps required to use the DEAPServer class:

#### Init Arguments:
- `algorithm_kwargs`: The algorithm arguments, these can be changed in the middle of a run
- `additional_settings` (optional): Pass any additional custom settings that you want to keep track off
- `title`: The title of your problem, ideally unique
- `initial_pop_size`: Population size at initialization, defaults to 100
- `stats`: Pass your `Statistics` object, uses default `Statistics` object by default
- `toolbox`: Pass your `Toolbox` object, uses default `Toolbox` object by default.
- `halloffame`: Pass your `HallOfFame` object, uses `HallOfFame` object with a size of 1 by default
- `host`: host of the server. `localhost` by default
- `port`: port of the server. `8080` by default
- `general_stats_provider` (optional): provider of the generic statistics (refer to the Generic Protocol). Takes a `GADataDeap` as parameter, and must return a serializable `dict`
- `settings`: A list of `DeapSetting`, which contain info, handlers and getters for the settings. Some presets are already present in [this file](./ga_server/deap_server/deap_settings_presets.py)
- `algorithm`: The algorithm that you want to use. FIrst argument of this function is the population, the second is the toolbox, and as a named argument, it should be able to handle halloffame
- `individual_encoding`: The encoding of the individuals. You have a choice betweem indexes, range, and boolean. You can use the functions in [this file](./ga_server/deap_server/individual_encoding.py)

#### Adding the basic functions

I would suggest checking and being somewhat familiar with the DEAP documentation before continuing.

Your toolbox in the server should contain the following functions:
- `population`: returns the population given the number of individuals
- `evaluate`: returns the fitness as a tuple given an individual
- `mutate`: returns a mutated individual given the original individual
- `mate`: returns the result of a crossover between two indivudals
- `select`: selects k individuals from a population and returns them in a list.

These functions should respect the format used by DEAP.

⚠️ Warning ⚠️ Individuals in the population should contain the `visualization_data` field with the `IndividualData` type. This can easily be added by using the `DEAPServer.create` to create your Individual class.

#### Running the server

The server is then run using the `DEAPServer.run` function. It will exit when user sends Interrupt signal using `Ctrl+C` on linux for example.