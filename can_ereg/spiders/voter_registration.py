# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser


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
                '__SCROLLPOSITIONX': '0',
                '__SCROLLPOSITIONY': '0',
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucPerson$fldFirstName$txtField': 'Patrick',
                'ctl00$ContentPlaceHolder1$ucPerson$fldMiddleName$txtField': '',
                'ctl00$ContentPlaceHolder1$ucPerson$fldLastName$txtField': 'Connolly',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateYear$ddField': '1985',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateMonth$ddField': '3',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateDay$ddField': '17',
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': 'M6G1L5',
                'ctl00$ContentPlaceHolder1$ucAddress$fldStreet$ddField': '92774',
                'ctl00$ContentPlaceHolder1$ucAddress$fldCivic$txtField': '719',
                'ctl00$ContentPlaceHolder1$ucAddress$fldSuffix$ddField': '',
                'ctl00$ContentPlaceHolder1$ucAddress$fldUnit$txtField': '117',
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$ucAddress$BtnPostalCode'},
                callback=self.render_url,
                )

    def submit_voter_info(self, response):
        option_values = response.css('#ContentPlaceHolder1_ucAddress_fldStreet_ddField option::attr(value)').extract()
        formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': response.css('#__VIEWSTATE::attr(value)').extract_first(),
                '__SCROLLPOSITIONX': '0',
                '__SCROLLPOSITIONY': '0',
                '__EVENTVALIDATION': response.css('#__EVENTVALIDATION::attr(value)').extract_first(),
                'ctl00$ContentPlaceHolder1$ucPerson$fldFirstName$txtField': 'Patrick',
                'ctl00$ContentPlaceHolder1$ucPerson$fldMiddleName$txtField': '',
                'ctl00$ContentPlaceHolder1$ucPerson$fldLastName$txtField': 'Connolly',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateYear$ddField': '1985',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateMonth$ddField': '3',
                'ctl00$ContentPlaceHolder1$ucPerson$fldDateDay$ddField': '17',
                'ctl00$ContentPlaceHolder1$ucAddress$fldPostalCode$txtField': 'M6G1L5',
                'ctl00$ContentPlaceHolder1$ucAddress$fldStreet$ddField': option_values[1],
                'ctl00$ContentPlaceHolder1$ucAddress$fldCivic$txtField': '719',
                'ctl00$ContentPlaceHolder1$ucAddress$fldSuffix$ddField': '',
                'ctl00$ContentPlaceHolder1$ucAddress$fldUnit$txtField': '117',
                }
        yield FormRequest.from_response(
                response,
                formdata=formdata,
                formcss='#form1',
                clickdata={'name':'ctl00$ContentPlaceHolder1$NavButton$BtnNext'},
                callback=self.render_url,
                )

    def render_url(self, response):
        open_in_browser(response)
