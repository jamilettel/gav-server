from typing import List
from ga_server.deap_server.deap_settings import DeapSetting
from ga_server.deap_server.ga_data_deap import GADataDeap

def gen_getter_algorithm_kwargs(property: str):
    def getter_algorithm_kwargs(ga_data: GADataDeap):
        return ga_data.algorithm_kwargs[property]
    return getter_algorithm_kwargs

def gen_setter_algorithm_kwargs(property: str):
    def getter_algorithm_kwargs(ga_data: GADataDeap, value):
        ga_data.algorithm_kwargs[property] = value
    return getter_algorithm_kwargs

def get_cxpb_deap_setting(
    name: str = 'Crossover probability',
    min_increment: float = 0.1,
    setting_range: List[float] = [0.0, 1.0],
):
    return DeapSetting(
        setting_type='number',
        name=name,
        min_increment=min_increment,
        setting_range=setting_range,
        get_value=gen_getter_algorithm_kwargs('cxpb'),
        handler=gen_setter_algorithm_kwargs('cxpb'),
    )

def get_mutpb_deap_setting(
    name: str = 'Mutation probability',
    min_increment: float = 0.1,
    setting_range: List[float] = [0.0, 1.0],
):
    return DeapSetting(
        setting_type='number',
        name=name,
        min_increment=min_increment,
        setting_range=setting_range,
        get_value=gen_getter_algorithm_kwargs('mutpb'),
        handler=gen_setter_algorithm_kwargs('mutpb'),
    )

def get_mu_deap_settings(
    name: str = 'Population size',
    min_increment: int = 1,
    setting_range: List[int] = [0,1000],
):
    return DeapSetting(
        setting_type='number',
        name=name,
        min_increment=min_increment,
        setting_range=setting_range,
        get_value=gen_getter_algorithm_kwargs('mu'),
        handler=gen_setter_algorithm_kwargs('mu'),
    )

def get_lambda_deap_settings(
    name: str = 'Offspring population size',
    min_increment: int = 1,
    setting_range: List[int] = [0,1000],
    ):
    return DeapSetting(
        setting_type='number',
        name=name,
        min_increment=min_increment,
        setting_range=setting_range,
        get_value=gen_getter_algorithm_kwargs('lambda_'),
        handler=gen_setter_algorithm_kwargs('lambda_'),
    )
