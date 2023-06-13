from typing import Dict
from flask import Response

from app.lang_wizard import LangWizard
from app.login import is_logged_in
from app.database_adapters import PineconeDatabaseAdapter, JsonAdapter, ConfigAdapter
from app.openai_utils import get_openai_embeddings
from app.ai_construct import AIConstruct

from config import GameConfigurations, PineconeConfig


def ai_wrap(request, endpoint_name):
    """ Endpoints for ai streams generated with a single line. """
    token = request.cookies.get('token')
    claims = is_logged_in(token)
    if claims is None:
        def login_generator():
            yield "Please login.  I have to keep track of my followers."
        return Response(login_generator(),
                        mimetype='text/event-stream',
                        headers={'X-Accel-Buffering': 'no',
                                 'Access-Control-Allow-Origin': '*'})

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

    def response_generator(output: Dict):
        for chunk in output['prompt']:
            yield chunk

    return Response(response_generator(output),
                    mimetype='text/event-stream',
                    headers={'X-Accel-Buffering': 'no',
                             'Access-Control-Allow-Origin': '*'})
