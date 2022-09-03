from wsgiref import headers
from flask import Flask
from dotenv import load_dotenv
from typeform import Typeform
from twilio.rest import Client
import googlemaps
import os
import geopy

app = Flask(__name__)

load_dotenv('.env')
TYPEFORM = os.getenv('TYPEFORM')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
MAPS_KEY = os.getenv('MAPS_KEY')

@app.route('/start/<name>/<address>/<datetime>')
def start(name, address, datetime):
    url = "https://api.typeform.com/forms"

    form = {}
    form["title"] = "Test Form Carpool"
    form["type"] = "form"
    form["fields"] = [
        {
            "title": f"Can you attend {name} at {address} on {datetime}",
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
    groups = processData(res)
    return groups

def processData(data):   
    people = []
    drivers = []
    gmaps = googlemaps.Client(key=MAPS_KEY)

    # Process form data
    for response in data['items']:
        geocode = gmaps.geocode(response['answers'][2]['text'])[0]['geometry']['location']
        print(response['answers'][3]['boolean'])
        if response['answers'][3]['boolean']:
              drivers.append({
                'phone': response['answers'][1]['phone_number'],
                'name': response['answers'][0]['text'],
                'coordinates': geocode,
                'seats': response['answers'][4]['number']
              })
        else:
            people.append({
                'phone': response['answers'][1]['phone_number'],
                'name': response['answers'][0]['text'],
                'coordinates': geocode,
                'seats': response['answers'][4]['number']
                })

        groups = {}
        spots = {}
        while drivers:
            driver = drivers.pop(0)
            if not driver['name'] in groups:
                groups[driver['name']] = [driver]
                spots[driver['name']] = driver['seats']+1
            if len(groups[driver['name']]) < spots[driver['name']] and people:
                closest = people[0]
                for person in people:
                    if geopy.distance.distance(driver['coordinates']['lat']['lng'], person['coordinates']['lat']['lng']) < geopy.distance.distance(driver['coordinates']['lat']['lng'], closest['coordinates']['lat']['lng']):
                        closest = person
                groups[driver].append(closest)
                people.remove(closest)
                drivers.append(driver)
        if people:
            return {}
        return groups