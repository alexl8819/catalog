# catalog
Sample CRUD App

# Configuration
Overwrite the existing configuration `catalog.cfg` by doing the following:

- Set a unique `SECRET_KEY` for sessions
- Obtain OAuth 2.0 client Credentials (client id and secret) from Google's APIs Console to authenticate users logging in. 
[Learn more by visiting this link](https://developers.google.com/identity/protocols/OAuth2WebServer).
- Set the required `GOOGLE_` prefixed keys with the credentials obtained

# Install
Requires Python 2.6+ or Python 3+ and Node.js v6+

	$ unzip catalog.zip && cd catalog
	$ pip install -r requirements.txt
	$ npm install

# Usage
For production

	$ npm run start

For development

	$ npm run start:dev

# Test
Test will run pylint, check for pep8 compliance and validate CSS

	$ npm run test

# Heroku
See a [live demo here](https://vast-crag-79276.herokuapp.com)

# License
MIT
