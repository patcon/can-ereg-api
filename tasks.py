from celery import Celery

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapyscript import Job, Processor
from can_ereg.spiders.voter_registration import VoterRegistrationSpider


app = Celery('tasks', backend='redis://localhost:6379/1', broker='redis://localhost:6379/0')

@app.task
def check_registration(voter_data=None):
    job = Job(VoterRegistrationSpider(), payload=voter_data)
    response = Processor(get_project_settings()).run(job)

    return response
