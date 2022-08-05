from typing_extensions import Self
from deap import algorithms, base, tools
from typing import Any, List
from ga_server.deap_server.deap_settings import DeapSetting

def isnum(var):
    return type(var) is float or type(var) is int

class GADataDeap:

    def __init__(
        self,
        pop,
        toolbox: base.Toolbox,
        algorithm_kwargs: dict,
        stats: tools.Statistics,
        mate_settings: List[str],
        mutate_settings: List[str],
        select_settings: List[str],
        mate_default: str,
        mutate_default: str,
        select_default: str,
        hof: tools.HallOfFame,
        settings: List[DeapSetting],
        algorithm = algorithms.eaSimple,
    ):
        self.pop = pop
        self.toolbox = toolbox
        self.algorithm_kwargs = algorithm_kwargs
        self.stats = stats
        self.hof = hof
        self.generation = 0
        self.records: list[dict[str, Any]] = []
        self.mate_settings = mate_settings
        self.mutate_settings = mutate_settings
        self.select_settings = select_settings
        self.mate_value = mate_default
        self.mutate_value = mutate_default
        self.select_value = select_default
        self.settings = settings
        self.algorithm = algorithm
        self.add_default_settings()

    def add_default_settings(self):
        if len(self.mutate_settings) > 1:
            self.settings.append(DeapSetting(
                setting_type='string',
                name='Mutation',
                get_value=lambda ga_data: ga_data.mutate_value,
                handler=GADataDeap.upd_mutate,
                values=self.mutate_settings
            ))
        if len(self.mate_settings) > 1:
            self.settings.append(DeapSetting(
                setting_type='string',
                name='Crossover',
                get_value=lambda ga_data: ga_data.mate_value,
                handler=GADataDeap.upd_mate,
                values=self.mate_settings
            ))
        if len(self.select_settings) > 1:
            self.settings.append(DeapSetting(
                setting_type='string',
                name='Selection',
                get_value=lambda ga_data: ga_data.select_value,
                handler=GADataDeap.upd_select,
                values=self.select_settings
            ))

    ### Settings

    def upd_mate(ga_data: Self, setting_value):
        ga_data.mate_value = setting_value
        ga_data.toolbox.register("mate", getattr(ga_data.toolbox, f"mate_{setting_value}"))

    def upd_mutate(ga_data: Self, setting_value) -> bool:
        ga_data.mutate_value = setting_value
        ga_data.toolbox.register("mutate", getattr(ga_data.toolbox, f"mutate_{setting_value}"))

    def upd_select(ga_data: Self, setting_value) -> bool:
        ga_data.select_value = setting_value
        ga_data.toolbox.register("select", getattr(ga_data.toolbox, f"select_{setting_value}"))

    ### Utils

    def get_pop_data(self) -> List[dict]:
        return [{ 
            'Chromosome': ind.tolist(),
            'Fitness': sum(ind.fitness.wvalues) if len(ind.fitness.wvalues) > 0 else None
        } for ind in self.pop]

    ### Actions

    def run_one_gen(self) -> dict:
        self.algorithm(self.pop, self.toolbox, **self.algorithm_kwargs, ngen=1, halloffame=self.hof, verbose=False)

        record = self.stats.compile(self.pop)
        self.records.append(record)

        self.generation += 1
        return record

    ### Information

    def info(self) -> dict:
        popdata = self.get_pop_data()

        return {
            "all_stats": self.records,
            "population": popdata,
            "settings": self.get_settings()
        }

    def get_settings(self) -> dict:
        settings = {}
        for setting in self.settings:
            settings.update(setting.get_setting(self))
        return settings

    ### Settings handler
    
    def set_settings(self, command: dict) -> bool:
        if "setting_name" not in command or "setting_value" not in command:
            return False
        setting_name = command["setting_name"]
        setting_value = command["setting_value"]
        if type(setting_name) is not str:
            return False
        for setting in self.settings:
            if setting.name == setting_name:
                setting.set_setting(self, setting_value)
                return True
        return False

