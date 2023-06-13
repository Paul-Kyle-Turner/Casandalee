
from copy import deepcopy
import re
from typing import Dict, List, Union

from app.actions.action import Action
from app.langwizard_config import LangWizardConfig
from app.openai_utils import num_tokens_from_string


class PromptAction(Action):

    def __init__(self,
                 action_options: Dict,
                 action_name: str = "prompt",
                 action_id: str = "prompt"):
        super().__init__(action_options, action_name, action_id)

    def complete_action(self, langwizard_config):
        keyword_spy = langwizard_config.keyword_spy
        database_adapters = langwizard_config.database_adapters

        prompt = self.action_options['prompt']
        found_keywords = keyword_spy.search_for_keywords(prompt)
        keyword_replacements, _ = keyword_spy.query_keywords(found_keywords,
                                                             database_adapters)
        prompt = self.replace_prompt_text(
            prompt, keyword_replacements, langwizard_config)
        output = langwizard_config.ai_construct.chat(prompt, override=False)
        langwizard_config.outputs[self.action_id] = output

    def rollback_list(self,
                      replacement_list,
                      rollback_token_length: int = 3000) -> str:
        """ Generates a content replacement that is less than a 
            given size of tokens.
        """
        for i in range(len(replacement_list), 0, -1):
            content = ""
            for j in range(0, i, 1):
                content += str(replacement_list[j])
            if num_tokens_from_string(content, "cl100k_base") < rollback_token_length:
                return content.strip()
        return str(replacement_list[0]).strip()

    def replace_content_in_chat(self,
                                prompt: List[Dict],
                                keyword: str,
                                replacement_list: Union[List[str], str],
                                langwizard_config: LangWizardConfig) -> List[Dict]:
        """ 
        replaces a keyword in a prompt with either a rollback or with a the most likely answer. 
        """
        rollback_token_length = langwizard_config.rollback_token_length
        temp_prompt = []
        keyword_spy = langwizard_config.keyword_spy
        keyword_search_text = keyword_spy.surround_with_surrounding_special(
            keyword)
        for chat in prompt:
            content = chat['content']
            if re.search(keyword_search_text, chat['content']):
                if isinstance(replacement_list, str):
                    content = re.sub(keyword_search_text,
                                     replacement_list.strip(), content)
                else:
                    if rollback_token_length:
                        content = re.sub(keyword_search_text,
                                         self.rollback_list(replacement_list,
                                                            rollback_token_length),
                                         content)
                    else:
                        content = re.sub(keyword_search_text,
                                         str(replacement_list[0]).strip(),
                                         content)
            temp_chat = {
                "role": chat["role"],
                "content": content
            }
            temp_prompt.append(temp_chat)
        return temp_prompt

    def replace_prompt_text(self,
                            prompt: List[Dict],
                            keyword_replacements: Dict,
                            langwizard_config: LangWizardConfig) -> List[Dict]:
        """ replace keywords with the most likely replacement """
        copied_prompt = deepcopy(prompt)
        for keyword in langwizard_config.keyword_spy.keywords:
            try:
                copied_prompt = self.replace_content_in_chat(copied_prompt,
                                                             keyword,
                                                             keyword_replacements[keyword],
                                                             langwizard_config)
            except KeyError:
                # we loop through all of the keywords
                # the keywords may not exist yet, but that is fine.
                # just return the prompt and don't care about the missing keywords
                continue
        return copied_prompt


class CategoricalInterrogationAction(PromptAction):

    def __init__(self,
                 action_options: Dict,
                 action_name: str = "categorical_interrogation",
                 action_id: str = "categorical_interrogation"):
        super().__init__(action_options, action_name, action_id)
        self.store = self.action_options['store']
        self.key = self.action_options['key']

    def manual_rules(self, message, categories, manual_rules):
        message = message[0]
        found_categories = []
        for category in categories:
            try:
                for rule in manual_rules[category]:
                    rule_compile = re.compile(rule, re.IGNORECASE)
                    match = re.search(rule_compile, message)
                    if match:
                        found_categories.append(category)
            except KeyError:
                pass
        return list(set(found_categories))

    def manual_select(self, categories, database_adapters, keyword_spy, langwizard_config):
        manual_select_options = self.action_options['manual_select']
        ms_key = manual_select_options['key']
        ms_store = manual_select_options['store']
        ms_search = manual_select_options['search']
        database_adapter = database_adapters[ms_store]
        manual_rules = database_adapter.query(ms_key)

        search_keyword_config = keyword_spy.get_keyword_config(ms_search)
        search_database_store = search_keyword_config['store']
        search_database_adapter = database_adapters[search_database_store]
        search = search_database_adapter.query(ms_search)

        output = self.manual_rules(search, categories, manual_rules)
        langwizard_config.outputs[self.action_id] = output
        return output

    def manual_select_option(self, categories, database_adapters, keyword_spy, langwizard_config):
        manual_select_option = False
        will_break = False
        if 'manual_select' in self.action_options.keys():
            output = self.manual_select(categories,
                                        database_adapters,
                                        keyword_spy,
                                        langwizard_config)
            manual_select_option = True
            if 'break' in self.action_options['manual_select']:
                if self.action_options['manual_select']['break']:
                    will_break = True
        return manual_select_option, will_break, output

    def convert(self, output, langwizard_config, database_adapters):
        convert_key = self.action_options['convert']['key']
        convert_store = self.action_options['convert']['store']
        database_adapter = database_adapters[convert_store]
        convert_items = database_adapter.query(convert_key)
        output = self.retrieve_namespaces(output, convert_items)
        langwizard_config.outputs[self.action_id] = output
        return output

    @staticmethod
    def set_attr_safe(database_adapter, edit_atter, output, default):
        if output is None:
            setattr(database_adapter, edit_atter, default)
            return default
        attr = getattr(database_adapter, edit_atter)
        if not isinstance(output, type(attr)):
            setattr(database_adapter, edit_atter, default)
            return default
        if output:
            setattr(database_adapter, edit_atter, output)
            return output

    def complete_action(self, langwizard_config):
        keyword_spy = langwizard_config.keyword_spy
        database_adapters = langwizard_config.database_adapters

        category_database_adapter = database_adapters[self.store]
        categories = category_database_adapter.query(self.key)

        manual_select_option, will_break, output = self.manual_select_option(categories,
                                                                             database_adapters,
                                                                             keyword_spy,
                                                                             langwizard_config)
        convert_option = False
        if 'convert' in self.action_options.keys():
            convert_option = True

        edit_options = False
        if 'edit_options' in self.action_options.keys():
            edit_options = True

        if will_break:
            if convert_option:
                self.convert(output, langwizard_config, database_adapters)

            return

        prompt = self.action_options['prompt']
        found_keywords = keyword_spy.search_for_keywords(prompt)
        keyword_replacements, _ = keyword_spy.query_keywords(found_keywords,
                                                             database_adapters)
        prompt = self.replace_prompt_text(prompt,
                                          keyword_replacements,
                                          langwizard_config)

        output = langwizard_config.ai_construct.chat(prompt, override=True)
        output = self.clean_output(output)
        output = self.find_categories(output, categories)

        if manual_select_option:
            manual_output = langwizard_config.outputs[self.action_id]
            output = list(set(manual_output + output))

        if convert_option:
            output = self.convert(output, langwizard_config, database_adapters)

        if edit_options:
            edit_store = self.action_options['edit_options']['store']
            edit_attr = self.action_options['edit_options']['attr']
            default = self.action_options['edit_options']['default']
            database_adapter = database_adapters[edit_store]
            self.set_attr_safe(database_adapter, edit_attr, output, default)

    @staticmethod
    def clean_output(output: str) -> str:
        output = output.lower().strip()
        return re.sub(r'\.', '', output)

    def find_categories(self, output_message, categories):
        found_categories = []
        for category in categories:
            match = re.search(category, output_message, re.IGNORECASE)
            if match:
                found_categories.append(category)
        return found_categories

    def retrieve_namespaces(self, categories, selected_categories):
        namespaces = []
        for choice in categories:
            choice_compile = re.compile(choice, re.IGNORECASE)
            for namespace in list(selected_categories.keys()):
                match = re.search(choice_compile, namespace)
                if match:
                    namespaces.append(selected_categories[namespace])
        return namespaces
