from flask import Flask
app = Flask(__name__)

@app.route('/start')
def start():
    return 'Hello, World!'