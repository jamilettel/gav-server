
from copy import deepcopy
import json
from typing import Any, Dict, List, Tuple, Callable
from deap import base, tools, algorithms
from ga_server.deap_server.deap_settings import DeapSetting
from ga_server.deap_server.individual_encoding import get_ind_enc_indexes
from ga_server.gas import GAServer
from ga_server.deap_server.ga_data_deap import GADataDeap


class DEAPServer:

    def __init__(
        self,
        algorithm_kwargs: dict,
        title="Generic Genetic Algorithm",
        initial_pop_size=100,
        stats = tools.Statistics(),
        toolbox = base.Toolbox(),
        halloffame = tools.HallOfFame(1),
        host: str = "localhost",
        port: int = 8080,
        general_stats_provider: Callable[[Any, base.Toolbox, tools.HallOfFame], Dict] | None = None,
        algorithm = algorithms.eaSimple,
        settings: List[DeapSetting] = [],
        individual_encoding: dict[str,str] = get_ind_enc_indexes(),
    ) -> None:
        self.algorithm_kwargs = algorithm_kwargs
        self.toolbox = toolbox
        self.stats = stats
        self.pop = []
        self.hof = halloffame
        self.general_stats_provider = general_stats_provider
        self.title = title
        self.initial_pop_size = initial_pop_size
        self.host = host
        self.port = port

        self.mate_settings: List[str] = []
        self.mutate_settings: List[str] = []
        self.select_settings: List[str] = []

        self.mate_default = ""
        self.mutate_default = ""
        self.select_default = ""
        self.algorithm = algorithm
        self.settings = settings
        
        self.individual_encoding = individual_encoding

    def register_mate(self, name: str, function, default=False, *args, **kwargs):
        self.toolbox.register(f"mate_{name}", function, *args, **kwargs)
        self.mate_settings.append(name)
        if default:
            self.mate_default = name
            self.toolbox.register("mate", getattr(self.toolbox, f"mate_{name}"))

    def register_mutate(self, name: str, function, default=False, *args, **kwargs):
        self.toolbox.register(f"mutate_{name}", function, *args, **kwargs)
        self.mutate_settings.append(name)
        if default:
            self.mutate_default = name
            self.toolbox.register("mutate", getattr(self.toolbox, f"mutate_{name}"))

    def register_select(self, name: str, function, default=False, *args, **kwargs):
        self.toolbox.register(f"select_{name}", function, *args, **kwargs)
        self.select_settings.append(name)
        if default:
            self.select_default = name
            self.toolbox.register("select", getattr(self.toolbox, f"select_{name}"))


    def get_ga_data_provider(self):
        return lambda: GADataDeap(
            pop=self.toolbox.population(n=self.initial_pop_size),
            toolbox=deepcopy(self.toolbox),
            algorithm_kwargs=self.algorithm_kwargs,
            stats=deepcopy(self.stats),
            mate_settings=self.mate_settings,
            mutate_settings=self.mutate_settings,
            select_settings=self.select_settings,
            mate_default=self.mate_default,
            mutate_default=self.mutate_default,
            select_default=self.select_default,
            hof=deepcopy(self.hof),
            algorithm=deepcopy(self.algorithm),
            settings=deepcopy(self.settings),
        )

    def run(self):
        json_enc = json.encoder.JSONEncoder(separators=(',', ':'))

        def get_general_stats(ga_data: GADataDeap) -> Dict:
            general_stats = self.general_stats_provider(
                ga_data.pop, 
                ga_data.toolbox,
                ga_data.hof
            ) if self.general_stats_provider != None else {}
            return {
                **{
                    "Generation": str(ga_data.generation),
                    "Population": str(len(ga_data.pop))
                },
                **general_stats
            }

        def info(ga_data: GADataDeap, _) -> Tuple[str, bool]:
            return (json_enc.encode({
                "info": "all",
                "data": {
                    **{ "general_stats": get_general_stats(ga_data) },
                    **ga_data.info(),
                }
            }), False)

        def run_one_gen(ga_data: GADataDeap, _) -> Tuple[str, bool]:
            gen_stats = ga_data.run_one_gen()
            popdata = ga_data.get_pop_data()
            return (json_enc.encode({
                "info": "one-gen",
                "data": {
                    "general_stats": get_general_stats(ga_data),
                    "gen_stats": gen_stats,
                    "population": popdata
                }
            }), True)

        def settings(ga_data: GADataDeap, _) -> Tuple[str, bool]:
            return (json_enc.encode({
                "info": "settings-update",
                "settings": ga_data.get_settings()
            }), False)

        def set_setting(ga_data: GADataDeap, command: dict) -> Tuple[str, bool] | None:
            update = ga_data.set_settings(command)
            if update:
                return (settings(ga_data, {})[0], True)
            return None

        server: GAServer[GADataDeap] = GAServer(
            self.host,
            self.port,
            self.get_ga_data_provider(),
            commands = {
                "info": info,
                "run-one-gen": run_one_gen,
                "settings": settings,
                "set-setting": set_setting,
            },
            command_protocol = "generic",
            title=self.title
        )

        server.run()