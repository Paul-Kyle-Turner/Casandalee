"""
Main application of the rule lich.  

Author : Paul Turner
"""

from flask import Flask, render_template, request, jsonify

from app.login import is_logged_in
from app.lang_wizard import LangWizard
from app.hash_sha import hash_message_to_sha_256
from config import AppConfig

app = Flask(__name__)
wizard = LangWizard(AppConfig.DEAFULT_GAME, AppConfig.MAX_QUERY, AppConfig.STREAM)

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    claims = is_logged_in(id_token)
    return render_template('index.html', user_data=claims)


@app.route('/submit', methods=['POST'])
def submit():
    id_token = request.cookies.get('token')
    claims = is_logged_in(id_token)

    if claims is not None:
        try:

            data = request.get_json()
            message = data['message']
            message_hash = hash_message_to_sha_256(message)
            message_vector = wizard.get_embeddings(message, message_hash)
            namespaces = wizard.namespace_selection(message)
            content = wizard.query_question_with_namespaces_or_all_rollback(message, message_vector, namespaces)

            print(namespaces)
            print("at end")

            def response_generator(output):
                for chunk in output:
                    yield chunk

            if AppConfig.STREAM:
                print('stream')
                return app.response_class(response_generator(content), mimetype='text/event-stream', headers={'X-Accel-Buffering': 'no'})
            else:
                print('jsonify')
                return jsonify({"message": content})

        except Exception as e:
            return jsonify({"message": "Something went wrong, please contact the developer."})

    else:
        return jsonify({"message": "Please login to use this service."})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
