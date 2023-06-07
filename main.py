"""
Main application of dnd ai.
Author : Paul Turner
"""
from typing import Dict
from flask import Flask, render_template, request, Response

from app.lang_wizard import LangWizard
from app.login import is_logged_in
from app.database_adapters import PineconeDatabaseAdapter, JsonAdapter, ConfigAdapter
from app.openai_utils import get_openai_embeddings
from app.ai_construct import AIConstruct

from config import GameConfigurations, PineconeConfig


app = Flask(__name__)


@app.route('/')
def root():
    id_token = request.cookies.get("token")
    claims = is_logged_in(id_token)
    return render_template('index.html', user_data=claims)


@app.route('/lich', methods=["POST"])
def lich():
    json_data = request.get_json()

    ai_construct = AIConstruct({})
    config_adapter = ConfigAdapter(GameConfigurations.Pathfinder2e)
    json_adapter = JsonAdapter(json_data)
    pinecone_adapter = PineconeDatabaseAdapter(PineconeConfig,
                                               get_openai_embeddings,
                                               False)
    lang_wizard = LangWizard(ai_construct, {'pinecone': pinecone_adapter,
                                            'config': config_adapter,
                                            'json_input': json_adapter})

    output = lang_wizard.endpoint_response('lich')

    def response_generator(output: Dict):
        for chunk in output['prompt']:
            yield chunk

    return Response(response_generator(output),
                    mimetype='text/event-stream',
                    headers={'X-Accel-Buffering': 'no',
                             'Access-Control-Allow-Origin': '*'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
