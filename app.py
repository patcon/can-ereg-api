import connexion
import logging

from connexion import NoContent
from tasks import check_registration


def create_check(**data):
    # TODO: Fix in spider so this isn't required.
    data.update({'unit_number': ''})
    task = check_registration.delay(data)

    return {'status': task.status}

def get_check():
    return NoContent, 200

logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__, specification_dir='spec/')
app.add_api('swagger.yml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=5000, server='gevent')
