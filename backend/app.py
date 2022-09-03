from wsgiref import headers
from flask import Flask
from dotenv import load_dotenv
from typeform import Typeform
import os

app = Flask(__name__)

load_dotenv('.env')
TYPEFORM = os.getenv('TYPEFORM')

@app.route('/start')
def start():
    url = "https://api.typeform.com/forms"

    headers = {}
    headers["Authorization"] = f"Bearer {TYPEFORM}"

    form = {}
    form["title"] = "Test Form Carpool"
    form["type"] = "form"
    form["fields"] = [
        {
            "title": "Name",
            "type": "short_text",
            "validations": {
                "required": True
            }
        },
        {
            "title": "Phone Number",
            "type": "phone_number",
            "validations": {
                "required": True
            }
        },
        {
            "title": "Pickup Address?",
            "type": "short_text",
            "validations": {
                "required": True
            }
        },
        {
            "title": "Can you drive?",
            "type": "yes_no",
            "validations": {
                "required": True
            }
        },
        {
            "title": "If you can drive, how many passengers can you take?",
            "type": "number",
            "validations": {
                "required": True
            }
        }
    ]

    forms = Typeform(TYPEFORM).forms
    res = forms.create(form)
    

    return res['id']

@app.route('/stop/<form_id>')
def stop(form_id):
    forms = Typeform(TYPEFORM).responses
    res = forms.list(form_id)
    return res
