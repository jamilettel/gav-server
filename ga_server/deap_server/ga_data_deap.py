from copy import deepcopy
from typing_extensions import Self
from deap import algorithms, base, tools
from typing import Any, List, Literal
from .IndividualData import IndividualData
from ga_server.deap_server.deap_settings import DeapSetting

def isnum(var):
    return type(var) is float or type(var) is int

class GADataDeap:

    def __init__(
        self,
        pop,
        toolbox: base.Toolbox,
        algorithm_kwargs: dict,
        additional_settings: dict,
        stats: tools.Statistics,
        mate_settings: List[str],
        mutate_settings: List[str],
        select_settings: List[str],
        mate_default: str,
        mutate_default: str,
        select_default: str,
        hof: tools.HallOfFame,
        settings: List[DeapSetting],
        individual_encoding: dict[str, str],
        decorators: dict[str, list],
        algorithm = algorithms.eaSimple,
    ):
        self.pop = pop
        self.toolbox = toolbox
        self.algorithm_kwargs = algorithm_kwargs
        self.additional_settings = additional_settings
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
        self.individual_encoding = individual_encoding
        self.working = False
        self.settings_changelog = []
        self.populations = [deepcopy(self.pop)]
        self.decorators = decorators
        self.add_default_settings()
        self.add_settings_to_changelog()

    def add_settings_to_changelog(self):
        for setting in self.settings:
            self.settings_changelog.append({
                'generation': -1,
                'setting': setting.name,
                'value': setting.get_value(self),
            })

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
        ga_data.toolbox.unregister("mate")
        ga_data.toolbox.register("mate", getattr(ga_data.toolbox, f"mate_{setting_value}"))
        if "mate" in ga_data.decorators:
            for decorator in ga_data.decorators["mate"]:
                ga_data.toolbox.decorate("mate", decorator)

    def upd_mutate(ga_data: Self, setting_value) -> bool:
        ga_data.mutate_value = setting_value
        ga_data.toolbox.unregister("mutate")
        ga_data.toolbox.register("mutate", getattr(ga_data.toolbox, f"mutate_{setting_value}"))
        if "mutate" in ga_data.decorators:
            for decorator in ga_data.decorators["mutate"]:
                ga_data.toolbox.decorate("mutate", decorator)

    def upd_select(ga_data: Self, setting_value) -> bool:
        ga_data.select_value = setting_value
        ga_data.toolbox.unregister("select")
        ga_data.toolbox.register("select", getattr(ga_data.toolbox, f"select_{setting_value}"))
        if "select" in ga_data.decorators:
            for decorator in ga_data.decorators["select"]:
                ga_data.toolbox.decorate("select", decorator)

    ### Utils

    def get_pop_data(population) -> List[dict]:
        return [{
            "id": None,
            "chromosome": ind.tolist(),
            "fitness": sum(ind.fitness.wvalues) if len(ind.fitness.wvalues) > 0 else None,
            **ind.visualization_data.to_dict()
        } for ind in population]

    ### Actions

    def run_one_gen(self) -> dict:
        aged_ids = []
        for ind in self.pop:
            if ind.visualization_data.id not in aged_ids:
                ind.visualization_data.age += 1
                aged_ids.append(ind.visualization_data.id)
        self.algorithm(self.pop, self.toolbox, **self.algorithm_kwargs, halloffame=self.hof)
        self.populations.append(deepcopy(self.pop))

        record = self.stats.compile(self.pop)
        self.records.append(record)

        self.generation += 1
        return record

    ### Information

    def info(self) -> dict:
        return {
            "all_stats": self.records,
            "status": self.get_status(),
            "populations": [GADataDeap.get_pop_data(pop) for pop in self.populations],
            "settings": self.get_settings(),
            "individual_encoding": self.individual_encoding,
            "settings_changelog": self.settings_changelog
        }

    def get_settings(self) -> dict:
        settings = {}
        for setting in self.settings:
            settings.update(setting.get_setting(self))
        return settings

    ### Settings handler

    def set_settings(self, command: dict) -> bool:
        if "settings" not in command or type(command["settings"]) is not dict:
            return False
        for setting_name, setting_value in command["settings"].items():
            if type(setting_name) is not str:
                return False
            for setting in self.settings:
                if setting.name == setting_name:
                    if not setting.set_setting(self, setting_value):
                        return False
                    self.settings_changelog.append({
                        'generation': self.generation,
                        'setting': setting.name,
                        'value': setting.get_value(self),
                    })
                    break
        return True

    def get_status(self) -> Literal['working', 'idle']:
        return 'working' if self.working else 'idle'
