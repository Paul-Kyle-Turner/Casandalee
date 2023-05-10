
from app.pinecone_util import fetch_pinecone_embedding
from app.pinecone_util import query_pinecone, query_many
from app.pinecone_util import pinecone_message_upsert
from app.openai_util import get_openai_embeddings, num_tokens_from_string
from app.openai_util import openai_completion, openai_completion_stream

from config import GameConfigurations
import re
import time


class LangWizard:
    
    @staticmethod
    def _select_configuration(default_game, configurations_list):
        for config in configurations_list:
            if config.__name__ == default_game:
                return config

    def __init__(self, default_game, max_query, stream):
        self.max_query = max_query
        self.default_game = default_game
        self.stream = stream
        self.game_config = self._select_configuration(default_game, GameConfigurations.GAMES)
        self.lich_identity_message = self.system_message("You are the \"The Rule Lich\". Your job is to make rulings for Table Top Role-Playing Games.  Use the information provided from the books and resources to respond.")
        self.question_namespace = self.system_message(f'The request being made requires documents from these categories: {self.game_config.CATEGORIES}.  Respond with a list of categories where information could be found to help solve the request from only these categories.')
        self.only_list = self.system_message("Only respond with a list.  Do not use any other language, or anything outside of the categories provided.")
        
    @staticmethod
    def system_message(message):
        return {"role": "user", "content": message}
    
    @staticmethod
    def user_message(message):
        return {"role": "user", "content": message}
    
    def question_message(self, message, content):
        return {"role": "user", "content": f'Respond with details about the {self.game_config.__name__}, using : {content}\n It must answer this question : {message}'}
    
    @staticmethod
    def get_embeddings(message, message_hash):
        pinecone_responce = fetch_pinecone_embedding(message_hash, 'messages')
        if pinecone_responce:
            message_vector = pinecone_responce[message_hash]['values']
        else:
            message_vector = get_openai_embeddings(message)
            pinecone_message_upsert(message, message_vector)
        return message_vector
    
    def _deciper_lich_category(self, output_message):
        categories = []
        for category in self.game_config.CATEGORIES:
            cat_compile = re.compile(category, re.IGNORECASE)
            match = re.search(cat_compile, output_message)
            if match:
                categories.append(category)
        return categories
    
    def _manual_select(self, message):
        categories = []
        for category in self.game_config.CATEGORIES:
            cat_compile = re.compile(category, re.IGNORECASE)
            match = re.search(cat_compile, message)
            if match:
                categories.append(category)
        
        for category in self.game_config.CATEGORIES:
            try:
                for rule in self.game_config.MANUAL_RULES[category]:
                    rule_compile = re.compile(rule, re.IGNORECASE)
                    match = re.search(rule_compile, message)
                    if match:
                        categories.append(category)
            except KeyError:
                pass
        return categories
    
    def _retrieve_namespaces(self, game_choices):
        namespaces = []
        for choice in game_choices:
            choice_compile = re.compile(choice, re.IGNORECASE)
            for namespace in list(self.game_config.NAMESPACES.keys()):
                match = re.search(choice_compile, namespace)
                if match:
                    namespaces.append(self.game_config.NAMESPACES[namespace])
        return namespaces
                
    def namespace_selection(self, message):
        manual_output = self._manual_select(message)
        if manual_output:
            return self._retrieve_namespaces(manual_output)
        else:
            messages = [
                self.lich_identity_message,
                self.question_namespace,
                self.only_list,
                self.user_message(message)
            ]
            output = openai_completion(messages).lower()
            output = output.strip()
            output = re.sub(r'\.', '', output)
            output = self._deciper_lich_category(output)
            output = list(set(manual_output + output))
            output = self._retrieve_namespaces(output)
        return output
    
    def _gather_match_content(self, matches):
        content = ''
        for match in matches:
            content += match['metadata']['content']
        return content

    def batch_or_stream_return(self, messages):
        if self.stream:
            print("in streaming")
            return openai_completion_stream(messages)
        else:
            print("in batch")
            return openai_completion(messages)

    def query_all_namespace(self, message, message_vector, top_k=3):
        matches = query_pinecone(message_vector, 
                                 self.game_config.CATEGORIES[self.game_config.ALL], 
                                 top_k)
        content = self._gather_match_content(matches)
        messages = [
            self.lich_identity_message,
            self.question_message(message, content)
        ]
        return self.batch_or_stream_return(messages)

    
    def query_question_with_namespaces_or_all_rollback(self, message, message_vector, namespaces):
        matches = query_many(message_vector, namespaces, top_k=1)
        content = self._gather_match_content(matches)
        if num_tokens_from_string(content) < 7000:
            print("in message back")
            messages = [
                self.lich_identity_message,
                self.question_message(message, content),
            ]
            return self.batch_or_stream_return(messages)
        else:
            for i in range(self.max_query, 0, -1):
                matches = query_pinecone(message_vector,
                                         self.game_config.CATEGORIES[self.game_config.ALL],
                                         top_k=i)
                content = self._gather_match_content(matches)
                if num_tokens_from_string(content) < 7000:
                    print("in message back all")
                    messages = [
                        self.lich_identity_message,
                        self.question_message(message, content)
                    ]
                    return self.batch_or_stream_return(messages)
                
    
    