from wsgiref import headers
from flask import Flask
from dotenv import load_dotenv
from typeform import Typeform
from twilio.rest import Client
import googlemaps
import os

app = Flask(__name__)

load_dotenv('.env')
TYPEFORM = os.getenv('TYPEFORM')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
MAPS_KEY = os.getenv('MAPS_KEY')

@app.route('/start/<name>/<address>/<time>/<phone>')
def start(name, address, time):
    url = "https://api.typeform.com/forms"

    form = {}
    form["title"] = "Test Form Carpool"
    form["type"] = "form"
    form["fields"] = [
        {
            "title": "Can you attend the event?",
            "type": "short_text",
            "validations": {
                "required": True
            }
        },
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
    processData(res)
    return res

def processData(data):   
    groups = []
    gmaps = googlemaps.Client(key=MAPS_KEY)
    for response in data['items']:
       geocode_result = gmaps.geocode(response['answers'][2]['text'])
       print(geocode_result)

