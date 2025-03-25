# candeebee - Greg Sloan

## Overview
This is a web-app developed by Greg Sloan as a simple environment to practice various technologies. 
It runs as a Python/Flask server and a JavaScript client browser app and provides an API 

The App itself is the "CanDeeBee" (Aka, the Candy Database). 
It is envisioned as a repository of various types of candybars and other 
candies on the market, with details about what each candy is made of (its "components"). 
In this basic form, it is a static list that lets you select one of the items 
and display its properties.

This repository incorporates LaunchDarkly feature flag capabilities to demonstrate
gating a feature (comments) behind a feature flag, targeting the feature to an
individual user context, and targeting the feature to a group of users defined
by a rule

## Deploy and Operate

### Environment Pre-Reqs
* Install python3 (developed and tested on v3.9.6)
* Install terraform (developed and tested on v1.11.12)
* Git - clone this repository
* An active LaunchDarkly account with a valid API Access token with Writer permission
* Access to 2 or 3 different browsers (e.g. Chrome and Safari on the same system, or 
  Chrome and Safari on one system + Chrome on a second system with local network access 
  to port 5000 on the system running the application)

### Prepare LaunchDarkly Project
* `cd terraform`
* `mv terraform.TEMPLATEtfvars terraform.tfvars`
* Change the line `launchdarkly_access_token = "<enter your access token>"` 
replacing `<enter your access token>` with your LaunchDarkly API access token
* `mv main.Deploy main.tf`
* `terraform init`
* `terraform plan`
* `terraform apply`
  * This will create a new LaunchDarkly Project (key=can-dee-bee), 
    and a boolean flag (key=candy-comments). 
  * The terraform outputs the client-side-id for the Production environment. It
    is a "sensitive" parameter, so it will be obscured in the script output
  * To display it, `terraform output client_side_id`
* `cd ..`
* `mv .TEMPLATEenv .env`
  * This file has 2 export commands. One for the environment client-side-id and
    one for the API Access token. Replace both with your values

### Start candeebee web app
* `source .env`
* `cd server`
* `pip install -r requirements.txt` (or `python3 -m pip install  -r requirements.txt` or
   whichever invocation of pip works for your python3 environment)
* `python3 server.py`
  * NOTE: if your system already has something running on port 5000, edit servery.py and 
    modify the line `app.run(host='0.0.0.0', debug=True, port=5000)` to 
    use an available port
* Validate that http://localhost:5000
  * Should show a title, logo, username/user since in the top left,
    a dropdown list of candy names.
  * Selecting a candy name from the list should display a text box with
    details and an image
  * Loading from different browser should display different user name/user since
    in top left

### Part 1: Release and Remediate
We had a successful launch a while back, but our user base has not grown and engagement is down.
We would like to open a new revenue stream by serving ads on the site, but we need to generate
engagement. To that end we've been developing a Comment system to encourage community interaction.
It has been developed and is complete, but in production remains behind a feature flag. We are ready
to release it and will do so live without user interruption.

* in a separate Command Line window from the running server process, cd to the repo
* `source .env`
* `cd server`
* `python3 ld-control.py -t on -f candy-comments -p can-dee-bee -e production`

There should now be a Comment form below each displayed candy. Validate from all user browsers.
Users can input a comment, it will display below the input box, newest comment first.

But - uh oh - turns out providing anonymous, unmoderated comment capabilities has not been the positive
community-building experience we had been hoping! Better roll that change back ASAP

* `python3 ld-control.py -t on -f candy-comments -p can-dee-bee -e production`

The comment feature should no longer be available to any users

### Part 2A: Target Individual User Context
We still think this is the right way to go, but let's slow down and validate that thought.
We are going to enable it, but this time ONLY for our co-founder (user:Greg). He will spend
some time with the feature and decide if it's the right way to go.

* From the root of this repo, `cd terraform`
* `mv main.tf main.Deploy`
* `mv main.IndividualTarget main.tf`
* `terraform plan`
* `terraform apply`
* `cd ../server`
* `python3 ld-control.py -t on -f candy-comments -p can-dee-bee -e production`

Okay, now Greg has access to the feature to get a feel for it, but the rest of the use base
remains on the old version.

### Part 2B: Target a group of User Contexts based on a rule
Greg agrees that in the long run, having this feature will be a net positive but recognizes
that a set of community standards will be imperative to its success. Rather than try to define
those ourselves, he wants to solicit the opinions of trusted community members. 

Fortunately, prior to public release, we had made the app available to a small group of trusted
users. They can be easily identified by the date they became users, "user_since". We will enable
the feature for only users with a "user_since" date that is before we went public.

* return to the terraform directory
* `mv main.tf main.IndividualTarget`
* `mv main.RuleTarget main.tf`
* `terraform plan`
* `terraform apply`
  * This will set the flag state back to off
* `cd ../server`
* `python3 ld-control.py -t on -f candy-comments -p can-dee-bee -e production`

Now only users with an early enough user_since value will see the comment box. Open 3 unique 
browsers to see this in action.