
from typing import Dict
from app.ai_adapters import OpenAIAdapter
from config import OpenAIConfig

class AIConstruct:

    def __init__(self,
                 ai_adapters:Dict,
                 stream:bool=True):
        if not ai_adapters:
            ai_adapters = {"openai": OpenAIAdapter(OpenAIConfig)}
        self.ai_adapters = ai_adapters
        self.stream = stream

    def select_ai_adapter(self, aiadapter:str):
        """ select between adapters or default first adapter """
        if aiadapter in self.ai_adapters:
            return self.ai_adapters[aiadapter]
        return self.ai_adapters[list(self.ai_adapters.keys())[0]]

    def batch_or_stream(self,
                        messages,
                        ai_adapter:str=None,
                        override:bool=False):
        """ return either a generator or a total piece of content """
        ai_adapter = self.select_ai_adapter(ai_adapter)
        if self.stream and not override:
            return ai_adapter.chat_stream(messages)
        return ai_adapter.chat(messages)

    def chat(self,
             messages,
             ai_adapter:str=None,
             override:bool=True):
        return self.batch_or_stream(messages, ai_adapter, override)
            