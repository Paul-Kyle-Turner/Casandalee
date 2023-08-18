
class LangWizardConfig:

    def __init__(self, 
                 ai_construct,
                 database_adapters,
                 endpoints,
                 keyword_spy,
                 rollback_token_length:int=3000):
        self.ai_construct = ai_construct
        self.database_adapters = database_adapters
        self.endpoints = endpoints
        self.keyword_spy = keyword_spy
        self.outputs = {}
        self.keyword_replacements = {}
        self.content_ids = {}
        self.rollback_token_length = rollback_token_length
