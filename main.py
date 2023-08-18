"""
Main application of dnd ai.
Author : Paul Turner
"""
import ast
from typing import Dict
from flask import Flask, render_template, request, Response, jsonify

from google.cloud import storage

from app.login import is_logged_in

from app.ai_wrap import ai_wrap

from app.ai_construct import AIConstruct
from app.database_adapters import PineconeDatabaseAdapter, JsonAdapter, ConfigAdapter
from app.lang_wizard import LangWizard
from app.openai_utils import get_openai_embeddings
from app.storage_adapters import GoogleBucketStorage

from config import AppConfig
from config import PineconeConfig
from config import GameConfigurations

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/backgrounds')
def backgrounds():
    return render_template('backgrounds.html')


@app.route('/content/content', methods=['POST'])
def content():
    token = request.cookies.get('token')
    claims = is_logged_in(token)
    if claims is None:
        def login_generator():
            yield "Please login.  I have to keep track of my followers."
        return Response(login_generator(),
                        mimetype='text/event-stream',
                        headers={'X-Accel-Buffering': 'no',
                                 'Access-Control-Allow-Origin': '*'})
    
    json_adapter = JsonAdapter(request.get_json())
    pinecone_adapter = PineconeDatabaseAdapter(PineconeConfig,
                                               get_openai_embeddings)

    storage_client = storage.Client()
    bucket_storage_adapter = GoogleBucketStorage(storage_client, AppConfig.CONTENT_BUCKET)

    content_response = bucket_storage_adapter.fetch([claims.get('email'),
                                            pinecone_adapter.create_id(json_adapter.query('message')[0])])

    content_response = ast.literal_eval(content_response)
    content_complete = []
    for content_key in content_response["prompt"]["content"].keys():
        content_result = pinecone_adapter.fetch_pinecone_embedding(content_response["prompt"]["content"][content_key],
                                                                   namespace=content_key)
        content_complete.append(content_result)

    content_urls = {}
    for content_item in content_complete:
        for content_key in content_item.keys():
            content_urls[content_item[content_key]['metadata']['title']] = content_item[content_key]['metadata']['url']

    return jsonify(content_urls)


@app.route('/chat/backgrounds', methods=['POST'])
def generate_backgrounds():
    token = request.cookies.get('token')
    claims = is_logged_in(token)
    if claims is None:
        def login_generator():
            yield "Please login.  I have to keep track of my followers."
        return Response(login_generator(),
                        mimetype='text/event-stream',
                        headers={'X-Accel-Buffering': 'no',
                                 'Access-Control-Allow-Origin': '*'})

    output = ai_wrap(request, 'backgrounds')

    def response_generator(output: Dict):
        for chunk in output['prompt']:
            yield chunk

    return Response(response_generator(output),
                    mimetype='text/event-stream',
                    headers={'X-Accel-Buffering': 'no',
                             'Access-Control-Allow-Origin': '*'})


@app.route('/report/chat', methods=['POST'])
def report_chat():
    token = request.cookies.get('token')
    claims = is_logged_in(token)
    if claims is None:
        return jsonify({"server-message": "Please login to use this service."})

    pinecone_adapter = PineconeDatabaseAdapter(PineconeConfig,
                                               get_openai_embeddings,
                                               global_index=False)

    storage_client = storage.Client()
    storage_adapter = GoogleBucketStorage(storage_client, AppConfig.JUDGE_BUCKET)

    json_data = request.get_json()
    message = json_data['message']
    message_hash = pinecone_adapter.create_id(message)
    response_message = json_data['response_message']
    response_hash = pinecone_adapter.create_id(response_message)
    judge = json_data['response_judge']

    storage_adapter.store(payload_json={"message": message, "response": response_message, "judge": judge},
                          keys=[message_hash, response_hash, claims.get("email")])

    if judge == "Good":
        return jsonify({"server-message": "Thank you for your response, we are glad the bot is working well."})
    return jsonify({"server-message": "Thank you for your response, we will update the bot with your recommendations."})


@app.route('/chat/rules', methods=['POST'])
def rules():
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

    output = lang_wizard.endpoint_response('rules')

    storage_client = storage.Client()
    bucket_storage_adapter = GoogleBucketStorage(storage_client, AppConfig.CONTENT_BUCKET)

    content_for_storage = lang_wizard.langwizard_config.content_ids

    def response_generator(output: Dict):
        for chunk in output['prompt']:
            yield chunk
        bucket_storage_adapter.store(payload_json=content_for_storage, keys=[claims.get('email'),
                                                                             pinecone_adapter.create_id(json_adapter.query('message')[0])])

    return Response(response_generator(output),
                    mimetype='text/event-stream',
                    headers={'X-Accel-Buffering': 'no',
                             'Access-Control-Allow-Origin': '*'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
