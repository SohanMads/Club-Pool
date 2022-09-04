from locale import format_string
from wsgiref import headers
from flask import Flask
from dotenv import load_dotenv
from typeform import Typeform
from twilio.rest import Client
import googlemaps
from datetime import datetime
import os
import requests
import json
from geopy import distance
app = Flask(__name__)

load_dotenv('.env')
TYPEFORM = os.getenv('TYPEFORM')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
MAPS_KEY = os.getenv('MAPS_KEY')

@app.route('/start/<name>/<lat>/<long>/<timestamp>')
def start(name, lat, long, timestamp):
    gmaps = googlemaps.Client(key=MAPS_KEY)
    address = gmaps.reverse_geocode((lat, long))[0]['formatted_address']
    date = datetime.fromtimestamp(int(timestamp))

    form = {}
    form["title"] = "Test Form Carpool"
    form["type"] = "form"
    form["fields"] = [
        {
            "title": f"Can you attend {name} at {address} on {date.strftime('%M/%Y, %I:%M %p')}?",
            "type": "yes_no",
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
    return {'id':res['id'], 'url':res['_links']['display']}

@app.route('/stop/<form_id>/<lat>/<long>/<timestamp>')
def stop(form_id, lat, long, timestamp):
    # forms = Typeform(TYPEFORM).responses
    res = get_responses(form_id)
    data = json.loads(res)
    groups = processData(data)
    textMembers((lat, long), timestamp, groups)
    return data


@app.route('/group/<form_id>')
def getGroups(form_id):
    forms = Typeform(TYPEFORM).responses
    data = forms.list(form_id)
    event = []
    drivers = 0
    passengers = 0
    for response in data['items']:
        print(response)
        if response['answers'][4]['boolean']:
            event.append({
                'phone': response['answers'][2]['phone_number'],
                'name': response['answers'][1]['text'],
                'seats': response['answers'][5]['number'],
                'isDriver': True
            })
            drivers += 1
        else:
            event.append({
                'phone': response['answers'][2]['phone_number'],
                'name': response['answers'][1]['text'],
                'seats': 0,
                'isDriver': False
                })
            passengers += 1
    return {
        'members': event,
        'drivers': drivers,
        'passengers': passengers
    }



def processData(data):   
    people = []
    drivers = []
    gmaps = googlemaps.Client(key=MAPS_KEY)
    # Process form data
    for rep in data['items']:
        geocode = gmaps.geocode(rep['answers'][3]['text'])[0]['geometry']['location']
        if rep['answers'][4]['boolean']:
            drivers.append({
                'phone': rep['answers'][2]['phone_number'],
                'name': rep['answers'][1]['text'],
                'coordinates': (geocode['lat'],geocode['lng']),
                'seats': rep['answers'][5]['number']
            })
            print(drivers[-1])
        else:
            people.append({
                'phone': rep['answers'][2]['phone_number'],
                'name': rep['answers'][1]['text'],
                'coordinates': (geocode['lat'],geocode['lng']),
                'seats': 0
                })
            print(people[-1])

    spots = {}
    groups = {}
    while drivers:
        driver = drivers.pop(0)
        if not driver['name'] in groups:
            groups[driver['name']] = [driver]
            spots[driver['name']] = driver['seats']+2
        if len(groups[driver['name']]) < spots[driver['name']] and people:
            closest = people[0]
            for i, person in enumerate(people):
                if distance.distance(driver['coordinates'], person['coordinates']) < distance.distance(driver['coordinates'], closest['coordinates']):
                    closest = person
            groups[driver['name']].append(closest)
            people.remove(closest)
            drivers.append(driver)
    if people:
        return {}
    return groups

def textMembers(dest, arrTime, groups):
    gmaps = googlemaps.Client(key=MAPS_KEY)
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    if not groups:
        return False
    for group in groups:
        waypoints = []
        for member in groups[group]:
            if not member['name'] == group:
                client.messages.create(
                    to=member['phone'],
                    from_="+19853226147",
                    body=f"Hello {member['name']}, you are in a carpool with {group}. Meet him at {gmaps.reverse_geocode(dest)[0]['formatted_address']} at {datetime.fromtimestamp(int(arrTime)).strftime('%I:%M %p')}."
                )
                waypoints.append(gmaps.reverse_geocode(member['coordinates'])[0]['formatted_address'])
            else:
                driver = member
        params={
            'api': 1,
            'origin': gmaps.reverse_geocode(driver['coordinates'])[0]['formatted_address'],
            'destination': gmaps.reverse_geocode(dest)[0]['formatted_address'],
            'waypoints': waypoints,
        }
        res = requests.get('https://www.google.com/maps/dir/', params=params)
        print(res.url)

        ppl = [x['name'] for x in groups[driver['name']]]
        pplStirng = ", ".join(ppl[1:-1]) + " and " + ppl[-1]
        client.messages.create(
            to=driver['phone'],
            from_="+19853226147",
            body = f"Hello {driver['name']}, you are driving a carpool. You will be picking up {pplStirng}. Use this link for directions: {res.url}"
        )
        return True

def get_responses(form_id):
    url = f"https://api.typeform.com/forms/{form_id}/responses"

    headers = {
    'Content-Type': 'text/plain',
    'Accept': 'application/json',
    'Authorization': f'Bearer {TYPEFORM}'
    }

    response = requests.request("GET", url, headers=headers)

    return response.text
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)