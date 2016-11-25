import scrapy

from celery import Celery
from os import environ
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapyscript import Job, Processor
from can_ereg.spiders.voter_registration import VoterRegistrationSpider


redis_url = environ['REDIS_URL']
app = Celery('tasks', backend='{}/1'.format(redis_url), broker='{}/0'.format(redis_url))

@app.task
def check_registration(voter_data=None):
    job = Job(VoterRegistrationSpider(), payload=voter_data)
    response = Processor(get_project_settings()).run(job)

    return response
