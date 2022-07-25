
from copy import deepcopy
import json
from typing import Any, Dict, List, Tuple, Callable
from deap import base, tools
from deap import tools
from ga_server.gas import GAServer
from ga_server.deap_server.ga_data_deap import GADataDeap

# def run_deap_server(
#     pop,
#     toolbox: base.Toolbox,
#     cxpb: float,
#     mutpb: float,
#     stats: tools.Statistics,
#     host: str = "localhost",
#     port: int = 8080,
#     title: str = "Generic Genetic Algorithm",
#     hof: tools.HallOfFame | None = None,
#     general_stats_provider: Callable[[Any, base.Toolbox, tools.HallOfFame], Dict] | None = None
# ):
#     json_enc = json.encoder.JSONEncoder()

#     def get_general_stats(ga_data: GADataDeap) -> Dict:
#         general_stats = general_stats_provider(ga_data.pop, ga_data.toolbox, ga_data.hof) if general_stats_provider != None else {}
#         return {
#             **{
#                 "Generation": str(ga_data.generation),
#             },
#             **general_stats
#         }

#     def info(ga_data: GADataDeap, _) -> Tuple[str, bool]:
#         return (json_enc.encode({
#             "info": "all",
#             "data": {
#                 **{ "general_stats": get_general_stats(ga_data) },
#                 **ga_data.info(),
#             }
#         }), False)

#     def run_one_gen(ga_data: GADataDeap, _) -> Tuple[str, bool]:
#         gen_stats = ga_data.run_one_gen()
#         return (json_enc.encode({
#             "info": "one-gen",
#             "data": {
#                 "general_stats": get_general_stats(ga_data),
#                 "gen_stats": gen_stats
#             }
#         }), True)

#     def settings(ga_data: GADataDeap, _) -> Tuple[str, bool]:
#         return (json_enc.encode({
#             "info": "settings",
#             "settings": ga_data.settings()
#         }), False)

#     def set_setting(ga_data: GADataDeap, command: dict) -> Tuple[str, bool] | None:
#         update = ga_data.set_settings(command)
#         if update:
#             return (settings(ga_data, {})[0], True)
#         return None

#     server: GAServer[GADataDeap] = GAServer(
#         host, 
#         port, 
#         ga_data_provider(pop, toolbox, cxpb, mutpb, stats, hof),
#         commands = {
#             "info": info,
#             "run-one-gen": run_one_gen,
#             "settings": settings,
#             "set-setting": set_setting,
#         },
#         command_protocol = "generic",
#         title=title
#     )

#     server.run()

class DEAPServer:

    def __init__(
        self, 
        cxpb=0.7, 
        mutpb=0.2,
        title="Generic Genetic Algorithm",
        initial_pop_size=100,
        stats = tools.Statistics(),
        toolbox = base.Toolbox(),
        halloffame = tools.HallOfFame(1),
        host: str = "localhost",
        port: int = 8080,
        general_stats_provider: Callable[[Any, base.Toolbox, tools.HallOfFame], Dict] | None = None,
    ) -> None:
        self.toolbox = toolbox
        self.stats = stats
        self.pop = []
        self.hof = halloffame
        self.cxpb = cxpb
        self.mutpb = mutpb
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
            self.toolbox.population(n=self.initial_pop_size),
            deepcopy(self.toolbox),
            self.cxpb,
            self.mutpb,
            deepcopy(self.stats),
            self.mate_settings,
            self.mutate_settings,
            self.select_settings,
            self.mate_default,
            self.mutate_default,
            self.select_default,
            hof=deepcopy(self.hof),
        )

    def run(self):
        json_enc = json.encoder.JSONEncoder()

        def get_general_stats(ga_data: GADataDeap) -> Dict:
            general_stats = self.general_stats_provider(
                ga_data.pop, 
                ga_data.toolbox,
                ga_data.hof
            ) if self.general_stats_provider != None else {}
            return {
                **{
                    "Generation": str(ga_data.generation),
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
            return (json_enc.encode({
                "info": "one-gen",
                "data": {
                    "general_stats": get_general_stats(ga_data),
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