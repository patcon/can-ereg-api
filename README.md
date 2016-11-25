# Canadian Voter Registration API

An API aspiring to offer a programmatic layer on top of the official
Election's Canada [Voter Registration tool](https://ereg.elections.ca/).

Working API available at
[can-ereg-api.herokuapp.com](https://can-ereg-api.herokuapp.com/).

## Anticipated Features

* [x] **Confirms voter registration info.** This is the bare minimum to make
  this interesting.
* [ ] **Updates voter registration info.** This is arguably a bad idea, but might
  be interesting. This would require submitting driver's license number.
* [ ] **Checks multiple addresses.** This will be helpful when you just want to
  submit your address history and find out where you're registered.
* [ ] **Allows access via API key.** We bypass Election Canada's captcha, so we'll
  need to restrict access to the API, contingent on developer account creation.
* [ ] **Accepts partial addresses.** We'll use the Google Maps geocoder to
  resolve them to full addresses for our lookup.

## Architecture

Since the form submission of the Elections Canada tool is a long-running
operation, we built this API around a Celery task queue. We made it as
RESTful as possible, given this constraint. Taking this approach, we
with `POST` to a `/checks` endpoint to queue a new check, and return a
resource identifier where the client will need to follow-up in order to
learn the result.

**Resources:**

* [RESTy Long-Ops](http://billhiggins.us/blog/2011/04/27/resty-long-ops/)
* [REST and Long-Running Jobs](http://farazdagi.com/blog/2014/rest-long-running-jobs/)
* [Open API standard](https://www.openapis.org/)

## Use-Cases

#### Alternative Voting System

Alice is building a [liquid
democratic](https://medium.com/@DomSchiener/liquid-democracy-true-democracy-for-the-21st-century-7c66f5e53b6f)
voting platform to help city councillors understand how citizens in
their districts feel about certain issues. A councillor needs to have
faith that that the information truthfully reflects the views of
citizens they represent. Alice's platform has Facebook integration, but
Alice has been told that councillors (rightfully) don't trust Facebook
names and addresses to be correct.

Thanksfully, Alice can use this **Voter Registration API** to improve
the situation. She can now add a layer of verification on accounts,
indicating when a Facebook account's address and name match a registered
voter. Now the councillors can have higher confidence that the data is
truly representative, and the citizen's views expressed via the platform
can be more fully respected.

#### Unofficial National Identity System

Bob wishes the Government of Canada offered a digital identity system,
but an official one is years away. But he's impatient, and wants to
start experimenting (as [Estonia has
done](https://e-estonia.com/e-residents/about/)) sooner rather than
later. He decides to bootstrap his own identity system, on which he can
experiment with offering cryptographic identities and authorize
third-party applications via OAuth, while ensuring each identity is
paired to a genuine citizen with reasonably high assurances.

Bob designs a system that allows people to enter the address at which
they're registered to vote. He confirms that this information matches a
registered voter via the **Voting Registration API**.  He then creates a
tentative user account, which is not yet activated.  Behind the scenes,
he then uses a simple postal API (like
[Lob](https://lob.com/services/postcards/pricing) to send postcards to
the registered address. The postcards include a code that can be used to
activate the account.


## Requirements

* Install [Redis](http://redis.io/topics/quickstart)
* Install [Heroku Command Line](https://devcenter.heroku.com/articles/heroku-command-line)

## Usage

    mkvirtualenv can-ereg-api --python=`which python3`
    pip install -r requirements.txt
    workon can-ereg-api

The automated voter registration check involves solving a captcha. This
can be done either (1) **manually** (default) or (2) **automatically**.
The former involves manually solving the captcha mid-scrape, by openning
it in its own window. The scraper waits until you submit a solution,
then continues. The latter automates this step by using
**[Anti-Captcha](https://anti-captcha.com)**, a captcha-solving service
that features API support. You can enable this by setting the
proper environment variable before running the scraper:

    export ANTICAPTCHA_API_KEY=<my-api-key>

For now scraper can be run directly, via queued celery task, or in full
as an API:

### Direct Scrape

    scrapy crawl voter_registration

### Queued Task

Since there can be no human interaction in a queued task, we must use
the Anti-Captcha service.

In one terminal, run the celery process:

    celery worker --app=tasks --loglevel=info

In another terminal, run:

    python example.py

### API

This is most easily run using Heroku CLI:

    # Set an environment variable that Heroku CLI will load
    echo ANTICAPTCHA_API_KEY=<my-api-key> > .env
    # Run the two processes from the Procfile
    huroku local

You can then explore the local API via:

    http://localhost:5000/
