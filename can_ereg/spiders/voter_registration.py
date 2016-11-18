# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
import logging
logger = logging.getLogger()


class VoterRegistrationSpider(scrapy.Spider):
    name = "voter_registration"
    allowed_domains = ["ereg.elections.ca"]
    start_urls = ['https://ereg.elections.ca/CWelcome.aspx']

    def parse(self, response):
        yield from self.submit_start(response)

    def submit_start(self, response):
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$NavButton$BtnNext'},
                callback=self.submit_privacy,
                )

    def submit_privacy(self, response):
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$NavButton$BtnNext'},
                callback=self.submit_eligibility,
                )

    def submit_eligibility(self, response):
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucYNCitizen$yn': 'rbYes',
                'ctl00$ContentPlaceHolder1$ucYNAge$yn': 'rbYes',
                'ctl00$ContentPlaceHolder1$ucYNAbroad$yn': 'rbYes',
                'ctl00$ContentPlaceHolder1$ucYNForces$yn': 'rbNo',
                'ctl00$ContentPlaceHolder1$TxtHHP': '',
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$NavButton$BtnNext'},
                callback=self.submit_postalcode,
                )

    def submit_postalcode(self, response):
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': 'M6G1L5',
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$ucAddress$BtnPostalCode'},
                callback=self.update_street,
                )

    def update_street(self, response):
        option_values = response.css('#ContentPlaceHolder1_ucAddress_fldStreet_ddField option::attr(value)').extract()
        formdata = {
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ucAddress$fldStreet$ddField',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': 'M6G1L5',
                'ctl00$ContentPlaceHolder1$ucAddress$fldStreet$ddField': option_values[1],
                }
        yield FormRequest(
                response.url,
                formdata=formdata,
                callback=self.submit_voter_info,
                )

    def submit_voter_info(self, response):
        option_values = response.css('#ContentPlaceHolder1_ucAddress_fldStreet_ddField option::attr(value)').extract()
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': 'M6G1L5',
                'ctl00$ContentPlaceHolder1$ucAddress$fldStreet$ddField': option_values[1],
                'ctl00$ContentPlaceHolder1$ucPerson$fldFirstName$txtField': 'Patrick',
                'ctl00$ContentPlaceHolder1$ucPerson$fldMiddleName$txtField': '',
                'ctl00$ContentPlaceHolder1$ucPerson$fldLastName$txtField': 'Connolly',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateYear$ddField': '1985',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateMonth$ddField': '3',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateDay$ddField': '17',
                'ctl00$ContentPlaceHolder1$ucAddress$fldCivic$txtField': '719',
                'ctl00$ContentPlaceHolder1$ucAddress$fldUnit$txtField': '117',
                'ctl00$ContentPlaceHolder1$NavButton$BtnNext': 'Next',
                }
        yield FormRequest(
                response.url,
                formdata=formdata,
                callback=self.solve_captcha,
                )

    def solve_captcha(self, response):
        # Can fetch this a few time and get different randomly-generated captchas to help make a better guess.
        # See: https://ereg.elections.ca/Telerik.Web.UI.WebResource.axd?type=rca&isc=true&guid=2d918a7f-09cb-4e0e-92e2-125d4ddb156a
        #captcha_rel_link = response.css('#ctl00_ContentPlaceHolder1_RadCaptcha1_CaptchaImage::attr(src)').extract_first()
        open_in_browser(response)

        self.crawler.engine.pause()
        captcha = input("Captcha: ")
        self.crawler.engine.unpause()

        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$txtCaptcha': captcha,
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$NavButton$BtnNextDelay'},
                callback=self.parse_vote_eligibility,
                )

    def parse_vote_eligibility(self, response):
        open_in_browser(response)
        text = response.css('.result > .firstchild > h2::text').extract_first().strip()
        logger.info(text)

    def render_url(self, response):
        open_in_browser(response)
