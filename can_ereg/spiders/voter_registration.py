# -*- coding: utf-8 -*-
import os
import scrapy
import urllib

from captcha_solver import CaptchaSolver
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser




class VoterRegistrationSpider(scrapy.Spider):
    name = "voter_registration"
    allowed_domains = ["ereg.elections.ca"]
    start_urls = ['https://ereg.elections.ca/CWelcome.aspx']
    default_voter_data = {
        'first_name': 'Patrick',
        'last_name': 'Connolly',
        'birth_date': '1985-3-17',
        'postal_code': 'M6G1L5',
        'street_number': '719',
        'unit_number': '117',
        }


    def parse(self, response):
        if hasattr(self, 'payload') and self.payload:
            self.voter_data = self.payload
        else:
            self.voter_data = self.default_voter_data
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
        # Extract address data from informal address using Google Maps API
        # See: https://developers.google.com/maps/documentation/geocoding/intro
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': self.voter_data['postal_code'],
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
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': self.voter_data['postal_code'],
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
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': self.voter_data['postal_code'],
                'ctl00$ContentPlaceHolder1$ucAddress$fldStreet$ddField': option_values[1],
                'ctl00$ContentPlaceHolder1$ucPerson$fldFirstName$txtField': self.voter_data['first_name'],
                'ctl00$ContentPlaceHolder1$ucPerson$fldMiddleName$txtField': '',
                'ctl00$ContentPlaceHolder1$ucPerson$fldLastName$txtField': self.voter_data['last_name'],
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateYear$ddField': self.voter_data['birth_date'].split('-')[0],
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateMonth$ddField': self.voter_data['birth_date'].split('-')[1],
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateDay$ddField': self.voter_data['birth_date'].split('-')[2],
                'ctl00$ContentPlaceHolder1$ucAddress$fldCivic$txtField': str(self.voter_data['street_number']),
                'ctl00$ContentPlaceHolder1$ucAddress$fldUnit$txtField': str(self.voter_data['unit_number']),
                'ctl00$ContentPlaceHolder1$NavButton$BtnNext': 'Next',
                }
        yield FormRequest(
                response.url,
                formdata=formdata,
                callback=self.solve_captcha,
                )

    def solve_captcha(self, response):
        if os.environ.get('ANTICAPTCHA_API_KEY'):
            solver = CaptchaSolver('antigate', api_key=os.environ['ANTICAPTCHA_API_KEY'])
        else:
            solver = CaptchaSolver('browser')

        # Can fetch this a few time and get different randomly-generated captchas to help make a better guess.
        # See: https://ereg.elections.ca/Telerik.Web.UI.WebResource.axd?type=rca&isc=true&guid=2d918a7f-09cb-4e0e-92e2-125d4ddb156a
        captcha_path = response.css('#ctl00_ContentPlaceHolder1_RadCaptcha1_CaptchaImage::attr(src)').extract_first()
        captcha_url = 'https://ereg.elections.ca/{}'.format(captcha_path)
        jpg_data = urllib.request.urlopen(captcha_url).read()

        self.crawler.engine.pause()
        captcha = solver.solve_captcha(jpg_data)
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
        text = response.css('.result > .firstchild > h2::text').extract_first().strip()
        # Expected options:
        #  - You are registered to vote, at the address you provided.
        #  - Based on the information provided, we cannot confirm that you are registered to vote.
        is_registered = True if ('You are registered to vote' in text) else False
        return {'raw_message': text, 'registered': is_registered}

    def render_url(self, response):
        open_in_browser(response)
