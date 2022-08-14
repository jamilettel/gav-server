
from copy import deepcopy
import json
from typing import Dict, List, Tuple, Callable
from deap import base, tools, algorithms, creator
from ga_server.deap_server.IndividualData import IndividualData
from ga_server.deap_server.deap_settings import DeapSetting
from ga_server.deap_server.individual_encoding import get_ind_enc_indexes
from ga_server.gas import GAServer
from ga_server.deap_server.ga_data_deap import GADataDeap


class DEAPServer:

    def __init__(
        self,
        algorithm_kwargs: dict={},
        additional_settings: dict={},
        title="Generic Genetic Algorithm",
        initial_pop_size=100,
        stats = tools.Statistics(),
        toolbox = base.Toolbox(),
        halloffame = tools.HallOfFame(1),
        host: str = "localhost",
        port: int = 8080,
        general_stats_provider: Callable[[GADataDeap], Dict] | None = None,
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
        self.additional_settings = additional_settings
        self.decorators: dict[str, list] = {}

    def create(
        name,
        base,
        **kwargs
    ):
        creator.create(name, base, **kwargs, visualization_data=IndividualData)

    def decorate(self, alias: str, *decorators):
        self.toolbox.decorate(alias, *decorators)
        if alias in self.decorators:
            self.decorators[alias] += list(decorators)
        else:
            self.decorators[alias] = list(decorators)

    def register_mate(self, name: str, function, default=False, *args, **kwargs):
        self.toolbox.register(f"mate_{name}", function, *args, **kwargs)
        self.mate_settings.append(name)
        if default or hasattr(self.toolbox, "mate") == False:
            self.mate_default = name
            if hasattr(self.toolbox, "mate"):
                self.toolbox.unregister("mate")
            self.toolbox.register("mate", getattr(self.toolbox, f"mate_{name}"))

    def register_mutate(self, name: str, function, default=False, *args, **kwargs):
        self.toolbox.register(f"mutate_{name}", function, *args, **kwargs)
        self.mutate_settings.append(name)
        if default or hasattr(self.toolbox, "mutate") == False:
            self.mutate_default = name
            if hasattr(self.toolbox, "mutate"):
                self.toolbox.unregister("mutate")
            self.toolbox.register("mutate", getattr(self.toolbox, f"mutate_{name}"))

    def register_select(self, name: str, function, default=False, *args, **kwargs):
        self.toolbox.register(f"select_{name}", function, *args, **kwargs)
        self.select_settings.append(name)
        if default or hasattr(self.toolbox, "select") == False:
            self.select_default = name
            if hasattr(self.toolbox, "select"):
                self.toolbox.unregister("select")
            self.toolbox.register("select", getattr(self.toolbox, f"select_{name}"))


    def get_ga_data_provider(self):
        return lambda: GADataDeap(
            pop=self.toolbox.population(n=self.initial_pop_size),
            toolbox=deepcopy(self.toolbox),
            algorithm_kwargs=deepcopy(self.algorithm_kwargs),
            additional_settings=deepcopy(self.additional_settings),
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
            individual_encoding=deepcopy(self.individual_encoding),
            decorators=self.decorators
        )

    def run(self):
        json_enc = json.encoder.JSONEncoder(separators=(',', ':'))

        def get_general_stats(ga_data: GADataDeap) -> Dict:
            general_stats = self.general_stats_provider(
                ga_data
            ) if self.general_stats_provider != None else {}
            return {
                **{
                    "Generation": str(ga_data.generation),
                    "Population": str(len(ga_data.pop))
                },
                **general_stats
            }

        def info(ga_data: GADataDeap, _command, _broadcast, send_to_client) -> Tuple[str, bool]:
            send_to_client(json_enc.encode({
                "info": "all",
                "data": {
                    **{ "general_stats": get_general_stats(ga_data) },
                    **ga_data.info(),
                }
            }))

        def run_one_gen(ga_data: GADataDeap, _command, broadcast, _send_to_client):
            gen_stats = ga_data.run_one_gen()
            popdata = GADataDeap.get_pop_data(ga_data.pop)
            broadcast(json_enc.encode({
                "info": "one-gen",
                "data": {
                    "general_stats": get_general_stats(ga_data),
                    "gen_stats": gen_stats,
                    "population": popdata
                }
            }))

        def get_settings(ga_data: GADataDeap):
            return json_enc.encode({
                "info": "settings-update",
                "settings": ga_data.get_settings()
            })

        def settings(ga_data: GADataDeap, _command, _broadcast, send_to_client):
            send_to_client(get_settings(ga_data))

        def get_settings_changelog(ga_data: GADataDeap):
            return json_enc.encode({
                "info": "settings-changelog",
                "settings_changelog": ga_data.settings_changelog
            })

        def send_settings_changelog(ga_data: GADataDeap, _command, _broadcast, send_to_client):
            send_to_client(get_settings_changelog(ga_data))

        def set_setting(ga_data: GADataDeap, command: dict, broadcast, _send_to_client) :
            update = ga_data.set_settings(command)
            if update:
                broadcast(get_settings(ga_data))
                broadcast(get_settings_changelog(ga_data))

        def get_status_string(ga_data: GADataDeap) -> str:
            return json_enc.encode({
                "info": "status",
                "status": ga_data.get_status()
            })

        def get_status(ga_data: GADataDeap, _command: dict, _broadcast, send_to_client):
            send_to_client(get_status_string(ga_data))

        def run_n_gen(ga_data: GADataDeap, command: dict, broadcast, send_to_client):
            n_gen = command["generations"]
            if type(n_gen) is not int or n_gen <= 0:
                return
            ga_data.working = True
            broadcast(get_status_string(ga_data))
            for _ in range(n_gen):
                run_one_gen(ga_data, {}, broadcast, send_to_client)
            ga_data.working = False
            broadcast(get_status_string(ga_data))

        self.decorate("mutate", IndividualData.mutate_decorator)
        self.decorate("mate", IndividualData.mate_decorator)

        server: GAServer[GADataDeap] = GAServer(
            self.host,
            self.port,
            self.get_ga_data_provider(),
            commands = {
                "info": info,
                "run-one-gen": run_one_gen,
                "settings": settings,
                "set-setting": set_setting,
                "get-status": get_status,
                "run-n-gen": run_n_gen,
                "settings-changelog": send_settings_changelog,
            },
            command_protocol = "generic",
            title=self.title
        )

        server.run()