import connexion
import logging

from connexion import NoContent
from flask import redirect
from os import environ
from tasks import check_registration


def create_check(**data):
    # TODO: Fix in spider so this isn't required.
    data.update({'unit_number': ''})
    task = check_registration.delay(data)

    response = {
            'status': task.status,
            'id': task.id,
            }

    return response, 202

def get_check(check_id):
    task = check_registration.AsyncResult(check_id)

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
