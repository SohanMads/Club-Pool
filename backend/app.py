from wsgiref import headers
from flask import Flask
from dotenv import dotenv_values
import requests
import os

app = Flask(__name__)

load_dotenv('.env')

TYPEFORM = os.getenv('TYPEFORM')

@app.route('/start')
def start():
    url = "https://api.typeform.com/forms"

    headers = {}
    headers["Authorization"] = "Bearer {TWILIO}"

    #resp = requests.get(url, headers=headers)