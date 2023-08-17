
from app.lang_wizard import LangWizard
from app.database_adapters import PineconeDatabaseAdapter, JsonAdapter, ConfigAdapter
from app.openai_utils import get_openai_embeddings
from app.ai_construct import AIConstruct

from config import GameConfigurations, PineconeConfig


def ai_wrap(request, endpoint_name):
    """ Endpoints for ai streams generated with a single line. """

    ai_construct = AIConstruct({})
    config_adapter = ConfigAdapter(GameConfigurations.Pathfinder2e)
    json_adapter = JsonAdapter(request.get_json())
    pinecone_adapter = PineconeDatabaseAdapter(PineconeConfig,
                                               get_openai_embeddings,
                                               global_index=False)
    lang_wizard = LangWizard(ai_construct, {'pinecone': pinecone_adapter,
                                            'config': config_adapter,
                                            'json_input': json_adapter})

    output = lang_wizard.endpoint_response(endpoint_name)

    return output
