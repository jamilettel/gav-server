from typing import Callable, List, Literal
from ga_server.deap_server.ga_data_deap import GADataDeap


def isnum(var):
    return type(var) is float or type(var) is int

class DeapSetting:
    """
    Setting class for the DEAP server.
    Contains functions to get and set value in the GAData,
    and constants such as type, values, range...
    """

    def __init__(
        self,
        setting_type: Literal['string', 'number'], 
        name: str,
        get_value: Callable[[GADataDeap], str | int | float],
        handler: Callable[[GADataDeap, str | int | float], None],
        setting_range: None | List[float] | List[int] = None,
    
        values: None | List[str] = None,
        min_increment: None | int | float = None,
    ):
        """
        Params:
        - setting_type: type of the setting
        - name: display name of the setting
        - get_value: getter for the value, given a GADataDeap object
        - handler: setter for the value, given a GADataDeap object and the user command. Handler shouldn't do any checking, already done in this class.
        - setting_range: array of length 2 if is a number, represents range of the setting
        - values: array of strings if is a string, represents the possible values of the setting
        - min_increment: number if setting is a number, represents the suggested increment for the UI
        """
        self.type = setting_type
        self.name = name
        self.get_value = get_value
        self.range = setting_range
        self.values = values
        self.handler = handler
        self.min_increment = min_increment

    def get_setting(self, ga_data: GADataDeap) -> dict:
        setting = {
            'type': self.type,
            'value': self.get_value(ga_data)
        }
        if self.type == 'string' and self.values is not None:
            setting['values'] = self.values
        if self.type == 'number':
            if self.min_increment is not None:
                setting['min_increment'] = self.min_increment
            if self.range is not None:
                setting['range'] = self.range
        return {
            self.name: setting
        }

    def check_number_command(self, value: str | int | float) -> bool:
        if not isnum(value):
            return False
        if self.range is not None and (value < self.range[0] or value > self.range[1]):
            return False
        return True
    
    def check_string_command(self, value: str | int | float) -> bool:
        if type(value) is not str:
            return False
        if self.values is not None and value not in self.values:
            return False
        return True

    def set_setting(self, ga_data: GADataDeap, value: str | int | float) -> bool:
        if self.type == 'number' and not self.check_number_command(value):
            return False
        elif self.type == 'string' and not self.check_string_command(value):
            return False
        self.handler(ga_data, value)
        return True
