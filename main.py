"""
Main application of dnd ai.
Author : Paul Turner
"""
from flask import Flask, render_template, request

from app.ai_wrap import ai_wrap

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


@app.route('/backgrounds', methods=['POST'])
def generate_backgrounds():
    return ai_wrap(request, 'backgrounds')


@app.route('/rules', methods=['POST'])
def rules():
    return ai_wrap(request, 'rules')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
