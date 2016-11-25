import connexion
import logging

from connexion import NoContent
from flask import redirect
from os import environ
from tasks import check_registration
from tasks import DEFAULT_STATE


def create_check(**data):
    # TODO: Fix in spider so this isn't required.
    data.update({'unit_number': ''})
    task = check_registration.delay(data)

    return NoContent, 202, {'Location': 'https://can-ereg-api.herokuapp.com/v1/checks/{}'.format(task.id)}

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
