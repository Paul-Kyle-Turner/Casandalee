# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import re
import time

from flask import Flask, render_template, request, jsonify
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token

import openai 
import pinecone
from util import hash_message_sha_256, craft_prompt, get_prompt

# firebase rest
firebase_request_adapter = requests.Request()

# datastore init
datastore_client = datastore.Client(project='dnd_lawyer')

#openai init
openai.api_key = os.getenv("OPENAI_API_KEY")

#pinecone init
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
index = pinecone.Index(os.getenv("PINECONE_NAME"))

app = Flask(__name__)

# Firestore
def store_time(email, dt):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'visit'));
    entity.update({
        'timestamp': dt
    });
    datastore_client.put(entity);

def store_user_message(email, message, dt):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'message'));
    entity.update({
        'timestamp': dt,
        'message': message
    });
    datastore.put(entity);

def fetch_times(email, limit):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='visit', ancestor=ancestor)
    query.order = ['-timestamp']
    times = query.fetch(limit=limit)
    return times

def fetch_user_message(email, limit):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='message', ancestor=ancestor)
    query.order = ['-timestamp']
    messages = query.fetch(limit)
    return messages

# pinecone insert
def pinecone_message_upsert(message, vector, namespace='messages'):
    message_dict = [{
        "id": hash_message_sha_256(message),
        "values": vector,
        "metadata": {
            "message": message
        }
    }]
    index.upsert(vectors=message_dict, namespace=namespace)

# pinecone fetch embedding
def fetch_pinecone_embedding(message_hash, namespace='messages'):
    return index.fetch(ids=[message_hash], namespace=namespace)['vectors']

# pinecone query embedding
def query_pinecone(vector, namespace='pathfinder2e-rules'):
    query_response = index.query(
        namespace=namespace,
        top_k=5,
        include_values=True,
        include_metadata=True,
        vector=vector)
    return query_response['matches']

# openai embeddings
def get_openai_embeddings(content, engine="text-embedding-ada-002"):
    content = content.encode(encoding="ASCII", errors="ignore").decode()  # fix unicode errors
    response = openai.Embedding.create(input=content, engine=engine)
    vector = response['data'][0]['embedding']
    return vector

# openai completion
def openai_completion( prompt, model="text-davinci-003", temperature=0, top_p=1.0, max_tokens=400, freq_pen=0.0, pres_pen=0.0, max_retry=5):
        retry = 0
        prompt = prompt.encode(encoding="ASCII", errors="ignore").decode()
        while True:
            try:
                response = openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=freq_pen,
                    presence_penalty=pres_pen
                )
                text = response["choices"][0]["text"].strip()
                text = re.sub(r'[\r\n]+', "\n", text)
                text = re.sub(r'[\t]+', " ", text)
                return text
                    
            except Exception as e:
                retry += 1
                if retry >= max_retry:
                    return f"GPT3 error: {e}"
                print("Error in communication with openai.")
                time.sleep(1)

# get embeddings from pinecone and if none exists create a new embedding with openai
def get_embedding(message, namespace='messages'):
    message_hash = hash_message_sha_256(message)
    pinecone_vector = fetch_pinecone_embedding(message_hash, namespace)
    if pinecone_vector:
        return pinecone_vector[message_hash]['values'], True
    else:
        return get_openai_embeddings(message), False

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    messages = None
    num_messages_sent = 0

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            # store_time(claims['email'], datetime.datetime.now(tz=datetime.timezone.utc))

            # messages = fetch_user_message(claims['email'], 10)
            # num_messages_sent = len(messages)

        except ValueError as exc:
            error_message = str(exc)

    return render_template('index.html',
                            user_data=claims,
                            error_message=error_message,
                            messages=messages,
                            num_messages_sent=num_messages_sent)


@app.route('/submit', methods=['POST'])
def submit():
    id_token = request.cookies.get('token')
    output = ""
    debug = ""

    if id_token or True:
        try:
            data = request.get_json()
            message = data['message']

            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            
            dt = datetime.datetime.now(tz=datetime.timezone.utc)
            # store_user_message(claims['email'], message, dt)

            debug += "past the claims\n"

            # embed message or get embeddings
            message_hash = hash_message_sha_256(message)
            debug += str(message_hash) + "\n"
            pinecone_vector = fetch_pinecone_embedding(message_hash, 'messages')
            debug += str(pinecone_vector) + "\n"
            if pinecone_vector:
                debug += "in pinecone vector"+ "\n"
                message_vector, is_stored = pinecone_vector[message_hash]['values'], True
            else:
                debug += "in openai vector"+ "\n"
                message_vector, is_stored = get_openai_embeddings(message), False
            debug += str(message_vector) + "\n"

            debug += "get the message vector\n"

            # if the embedding was not stored in pinecone upsert
            if not is_stored:
                debug += "pinecone upsert\n"
                pinecone_message_upsert(message, message_vector)

            # query pinecone for rules
            debug += "pinecone query 1\n"
            related_rules = query_pinecone(message_vector, namespace="pathfinder2e-rules")
            related_rules_text = "\n".join([x['metadata']['content'] for x in related_rules])

            # query pinecone for related messages
            debug += "pinecone query 2\n"
            related_messages = query_pinecone(message_vector, namespace="messages")
            related_messages_text = "\n".join([x['metadata']['message'] for x in related_messages])

            # craft a prompt
            debug += "prompt\n"
            prompt = get_prompt('prompt.txt')
            prompt = craft_prompt(prompt, message, related_rules_text, related_messages_text)

            # send the prompt to openai
            debug += "completion\n"
            output = openai_completion(prompt)

        except Exception as e:
            output = "Something went wrong please contact the developer."

    # Return a JSON response with a message
    response = {
                'message': output,
                'debug': debug
            }
    return jsonify(response)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
