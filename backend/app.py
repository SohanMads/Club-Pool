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

    form = {}
    form["title"] = "Test Form Carpool"
    form["type"] = "form"
    form["fields"] = [
        {
            "id": "Name",
            "title": "Name",
            "type": "short_text",
            "validations": True
        },
        {
            "id": "Phone",
            "title": "Phone Number",
            "type": "phone_number",
        }
    ]

    #resp = requests.post(url, data = form, headers=headers)