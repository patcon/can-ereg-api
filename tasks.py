from celery import Celery

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from can_ereg.spiders.voter_registration import VoterRegistrationSpider


app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def check_registration():
    process = CrawlerProcess(get_project_settings())
    process.crawl(VoterRegistrationSpider)
    process.start()
