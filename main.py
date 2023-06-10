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
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def root():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/lich', methods=["POST"])
def lich():
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
