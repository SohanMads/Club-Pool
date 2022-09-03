from ast import Num
from xmlrpc.client import boolean
from flask import Flask

app = Flask(__name__)

@app.route('/create-carpool', methods=['GET','POST'])
def create_carpool():
    if request.method == 'GET':
        return make_response('failure')
    if request.method == 'POST':
        address = request.json['address']
        name = request.json['name']
        driver = request.json['driver']
        people = request.json['people']

        create_row_data = {'name': str(name),'address':str(address),'driver':boolean(driver),'people':Num(people)}

        response = requests.post(
            url, data=json.dumps(create_row_data),
            headers={'Content-Type': 'application/json'}
        )
        return response.content

if __name__ == '__main__':
    app.run(host='localhost',debug=False, use_reloader=True)

