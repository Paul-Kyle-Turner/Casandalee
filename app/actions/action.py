
from typing import Dict

class Action:

    def __init__(self, action_options:Dict,
                 action_name:str="base_action",
                 action_id:str="base_action"):
        self.action_name = action_name
        self.action_options = action_options[action_name]
        self.action_id = action_id

    def complete_action(self, langwizard_config):
        raise NotImplementedError
