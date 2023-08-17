"""
Main application of dnd ai.
Author : Paul Turner
"""
from typing import Dict
from flask import Flask, render_template, request, Response, jsonify

from google.cloud import storage

from app.login import is_logged_in

from app.ai_wrap import ai_wrap
from app.database_adapters import PineconeDatabaseAdapter
from app.storage_adapters import GoogleBucketStorage
from app.openai_utils import get_openai_embeddings

from config import PineconeConfig
from config import AppConfig

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

    output = ai_wrap(request, 'rules')

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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
