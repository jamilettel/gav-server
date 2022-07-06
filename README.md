# Genetic Algorithm Visualizer Server

This server is used to compute and send information about a genetic algorithm. 
An example of a client that can use this server can be found
[here](https://www.github.com/jamilettel/gav-server).

## Starting the server

To install dependencies and start the server, you can use the following commands:

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
./tsp.py

```

[`tsp.py` ](./tsp.py) here is an example of how to setup and use the server when working with the Travelling Salesman Problem.

## Usage

To launch the server with the DEAP framework, you can use the run_deap_server function. You have to pass:
- population
- a toolbox containing at least `select`, `mate`, `mutate`, and `evaluate`
- crossover probability
- mutation probability
- stats (optional)

You can look at [`tsp.py` ](./tsp.py) for an example on how to use this server.