import scrapy

from celery import Celery
from celery import current_app
from celery import states
# `after_task_publish` is available in celery 3.1+
# for older versions use the deprecated `task_sent` signal
from celery.signals import after_task_publish
from os import environ
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapyscript import Job, Processor
from can_ereg.spiders.voter_registration import VoterRegistrationSpider


DEFAULT_STATE = states.PENDING

# See: https://stackoverflow.com/questions/9824172/find-out-whether-celery-task-exists
@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend

    backend.store_result(body['id'], None, "IN-PROGRESS")

redis_url = environ.get('REDIS_URL', 'redis://localhost:6379')
app = Celery('tasks', backend='{}/1'.format(redis_url), broker='{}/0'.format(redis_url))

@app.task
def check_registration(voter_data=None):
    job = Job(VoterRegistrationSpider(), payload=voter_data)
    response = Processor(get_project_settings()).run(job)

    return response
