
import re
from typing import Dict, List, Set

class KeywordSpy:

    def __init__(self,
                 keywords_config:Dict,
                 surrounding_special:str="{}"):
        self.keywords_config = keywords_config

        self.surrounding_special = surrounding_special
        self.keyword_index = {}
        self.keyword_intx = {}
        self.keywords = []
        self.keyword_replacements = {}

        for keyword_index, keyword_config in enumerate(self.keywords_config):
            keyword = list(keyword_config.keys())[0]
            self.keyword_index[keyword] = keyword_index
            self.keyword_intx[keyword_index] = keyword
            self.keywords.append(keyword)

    def surround_with_surrounding_special(self, text: str) -> str:
        """ Surrounding text around the prompt keywords """
        if self.surrounding_special == "()":
            return "\\" + self.surrounding_special[0] + text + "\\" + self.surrounding_special[1]
        return self.surrounding_special[0] + text + self.surrounding_special[1]

    def search_for_keywords(self, messages:List[Dict]) -> List[str]:
        """ Search the prompt and interrogation for keywords """
        keywords_surrounded = [self.surround_with_surrounding_special(k) for k in self.keywords]

        content = [message['content'] for message in messages]

        found = self.find_keywords(content, keywords_surrounded)
        found_words = [f[1: -1] for f in found]
        return found_words

    def get_keyword_store(self, keyword: str) -> str:
        """ Find which database a keyword should be extracted from """
        keyword_index = self.keyword_index[keyword]
        store = self.keywords_config[keyword_index][keyword]['store']
        return store

    @staticmethod
    def find_keywords(content: List[str], keywords: List[str]) -> Set:
        """ Find the set of keywords that appear in the text """
        found = []
        for text in content:
            for keyword in keywords:
                if re.search(keyword, text):
                    found.append(keyword)
        return set(found)

    def get_keyword_config(self, keyword: str) -> Dict:
        """ Congifuration of a keyword
            return keyword store and key 
        """
        keyword_index = self.keyword_index[keyword]

        store = self.keywords_config[keyword_index][keyword]['store']
        if 'key' in self.keywords_config[keyword_index][keyword].keys():
            key = self.keywords_config[keyword_index][keyword]['key']
        else:
            key = None

        if 'query_keyword' in self.keywords_config[keyword_index][keyword].keys():
            query_keyword = self.keywords_config[keyword_index][keyword]['query_keyword']
        else:
            query_keyword = None

        return {'keyword':keyword,
                'store':store,
                'key':key,
                'query_keyword':query_keyword}

    def get_query_message_from_keyword(self,
                                       config,
                                       database_adapters):
        if config['query_keyword'] is not None:
            keyword_config = self.get_keyword_config(config['query_keyword'])
            database_adapter = database_adapters[keyword_config['store']]
            return database_adapter.query(keyword_config['key'])[0]
        return config['key']

    def query_keywords(self,
                       found_keywords: List[str],
                       database_adapters: Dict):
        """ Using the appropriate database adapter get the details for a given keyword
            Note that per keyword if the keyword has the same database adapter
                the queries will be checked to see if the data already exists
                and if it does then it will not query again 
        """
        keyword_configs = []
        for keyword in found_keywords:
            keyword_configs.append(self.get_keyword_config(keyword))

        queried_databases = {}
        keyword_replacements = {}
        content_ids = {}

        for config in keyword_configs:
            store = config['store']
            database_adapter = database_adapters[store]

            if store in queried_databases:
                documents = queried_databases[store]
            elif config['keyword'] in self.keyword_replacements:
                documents = self.keyword_replacements[config['keyword']]
            else:
                query_message = self.get_query_message_from_keyword(config, database_adapters)
                documents = database_adapter.query(query_message)
                queried_databases[store] = documents

            content = database_adapter.pull_key_from_responses(documents, config['key'])
            keyword_replacements[config['keyword']] = content
            self.keyword_replacements.update(keyword_replacements)
            content_ids[config['keyword']] = database_adapter.pull_id_from_reponses(documents)
        return self.keyword_replacements, content_ids
