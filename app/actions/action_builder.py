
from typing import List

from app.actions.prompt import PromptAction, CategoricalInterrogationAction


class ActionNotFoundError(Exception):
    """Exception raised when Yaml key error is found, something is wrong with your yaml"""

    def __init__(self, message: str = "Failed to find action keyword.  Please use 'prompt', 'interrogate', or 'categorical_interrogate'"):
        super().__init__(message)


class ActionBuilder:

    def build_actions(self, endpoints_config: List):
        actions = []
        for action in endpoints_config:
            action_name = list(action.keys())[0]
            action_id = action_name
            if 'id' in action[action_name].keys():
                action_id = action[action_name]['id']
            if action_name == "categorical_interrogation":
                actions.append(CategoricalInterrogationAction(action,
                                                              action_name,
                                                              action_id))
            # elif action_name == "interrogation":
            #     actions.append(InterrorgateAction(action,
            #                                       action_name,
            #                                       action_id))
            elif action_name == "prompt":
                actions.append(PromptAction(action,
                                            action_name,
                                            action_id))
            else:
                raise ActionNotFoundError
        return actions
