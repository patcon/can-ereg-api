import connexion
import json
import logging
import re

from connexion import NoContent
from flask import redirect
from geopy import geocoders
from os import environ
from tasks import check_registration
from tasks import DEFAULT_STATE


host = environ.get('HOST', 'https://can-ereg-api.herokuapp.com')

def extract_geo_component(response, component):
    name = [c['long_name'] for c in response.raw['address_components'] if component in c['types']]
    return '' if not name else name[0]

def create_check(**data):
    # TODO: Fix in spider so this isn't required.
    data.update({'unit_number': ''})
    geocoder_res = None

    if data.get('full_address'):
        geocoder_res = geocoder_response(data['full_address'])
        geocoder_data = {
                'postal_code': extract_geo_component(geocoder_res, 'postal_code'),
                'street_name': extract_geo_component(geocoder_res, 'route'),
                'street_number': extract_geo_component(geocoder_res, 'street_number'),
                'unit_number': extract_geo_component(geocoder_res, 'subpremise'),
                }
        data.update(geocoder_data)

    task = check_registration.delay(data)

    data = {
            'check_id': task.id,
            'geocoded_data': geocoder_res.raw,
            'submitted_data': data,
            }

    headers = {
        'Location': '{}/v1/checks/{}'.format(host, task.id),
        }

    return data, 202, headers

def geocoder_response(full_address):
    full_address = normalize_address(full_address)
    g = geocoders.GoogleV3()
    response = g.geocode(full_address, components={'country':'CA'})

    return response

def normalize_address(full_address):
    """
    Converts a Toronto-specific shorthand for building unit numbers
    into a format that the GMaps geocoder understands.

    GMaps geocoder expects building units to be formatted like so:

        719 Bloor St W #117, Toronto, ON
        719 Bloor St W, Toronto, ON #117

    It does not know how to classify this shorthand:

        117-719 Bloor St W, Toronto, ON
    """
    match = re.match('^(?P<unit>\d+[A-Za-z]?)-(?P<rest>.+)$', full_address)
    if match:
        addr_unit = match.group('unit')
        addr_rest = match.group('rest')
        full_address = '{} #{}'.format(addr_rest, addr_unit)

    return full_address

def get_check(check_id):
    task = check_registration.AsyncResult(check_id)

    if task.status == DEFAULT_STATE:
        return NoContent, 422

    result = task.result[0] if task.ready() else None

    response = {
            'status': task.status,
            'result': result,
            }

    return response, 200

logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__, specification_dir='spec/')
app.add_api('swagger.yml')

@app.route('/')
def index():
    return redirect('/v1/ui')

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    app.run()
