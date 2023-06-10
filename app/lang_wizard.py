
from typing import Dict

from app.actions.action_builder import ActionBuilder
from app.ai_construct import AIConstruct
from app.keyword_spy import KeywordSpy
from app.langwizard_config import LangWizardConfig
from app.yaml_load import load_yaml


class LangWizard:

    def __init__(self,
                 ai_construct: AIConstruct,
                 database_adapters: Dict,
                 endpoints_file_path: str = 'endpoints.yaml'):
        configuration_yaml = load_yaml(endpoints_file_path)
        keyword_spy = KeywordSpy(configuration_yaml['keywords'])

        self.langwizard_config = LangWizardConfig(ai_construct,
                                                  database_adapters,
                                                  configuration_yaml['endpoints'],
                                                  keyword_spy)
        self.action_builder = ActionBuilder()

    def endpoint_response(self, endpoint_name: str):
        endpoint_config = self.langwizard_config.endpoints[endpoint_name]
        actions = self.action_builder.build_actions(endpoint_config)

        for action in actions:
            action.complete_action(self.langwizard_config)

        outputs = self.langwizard_config.outputs
        return outputs
