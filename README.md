# Canadian Voter Registration API

This is an attempt at writing an API that will hopefully make it
simpler to check Canadian Voter Registration.

For now, it is just a scraper that checks my own registration via the
official Elections Canada voter registration tool.

We have generated [aspirational API
documentation](http://petstore.swagger.io/?url=https://raw.githubusercontent.com/patcon/can-ereg-api/master/spec/swagger.json)
presented via a fancy browser UI using the [Open API
standard](https://www.openapis.org/).

## Anticipated Features

* **Checks multiple addresses.** This will be helpful when you just want to
  submit your address history and find out where you're registered.
* **Allows access via API key.** We bypass Election Canada's captcha, so we'll
  need to restrict access to the API.
* **Accepts partial addresses.** We'll use the Google Maps geocoder to
  resolve them to full addresses for our lookup.
* **Registers/updates voter information.** This is arguably a bad idea,
  but might be interesting.

## Architecture

Since the form submission of the Elections Canada tool is a long-running
operation, we will likely need to build this API around a task queue.
Taking this approach, we with `POST` to a `registration_check` endpoint,
so queue a new check, and return an indication of where the client will
need to follow-up in order to learn the results.

**Resources:**

* [RESTy Long-Ops](http://billhiggins.us/blog/2011/04/27/resty-long-ops/)
* [REST and Long-Running Jobs](http://farazdagi.com/blog/2014/rest-long-running-jobs/)

## Use-Case

Alice is building a polling platform to help city councillors understand
how citizens in their districts feel about certain issues. A councillor
needs to have faith that that the information truthfully reflects the
views of citizens they represent. Alice's platform has Facebook
integration, but Alice has been told that councillors (rightfully) don't
trust Facebook names and addresses to be correct.

Thanksfully, Alice can use this voter registration API to improve the
situation. She can now add a layer of verification on accounts,
indicating when a Facebook account's address and name match a registered
voter. Now the councillors can have higher confidence that the data is
truly representative, and the citizen's views expressed via the platform
can be more fully respected.
