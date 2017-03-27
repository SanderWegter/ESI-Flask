#!/usr/bin/env python
from esipy import App
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.exceptions import APIException
from flask import Flask, render_template, request, jsonify, session, redirect, escape, url_for
import json
import urllib2
import re
import requests

app = Flask(__name__)

if __name__ == '__main__':
	config = {}
	execfile("config.conf",config)
	serverIP = config['serverIP']
	serverPort = config['serverPort']

	debug = config['debug']

	app.secret_key = config['appKey']
	esi_app = App.create('https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility')

	security = EsiSecurity(
		app=esi_app,
		redirect_uri=config['callbackURL'],
		client_id=config['clientID'],
		secret_key=config['secretKey']
		)
	client = EsiClient(security=security)
	scopes = ['esi-location.read_location.v1']

#Example route to show how to grab data from ESI
@app.route('/getLocation')
def location():
	if 'char' in session:
		security.update_token(session['token'])
		security.refresh()
		verif = security.verify()

		charID = verif.get('CharacterID')
		charLocation = esi_app.op['get_characters_character_id_location'](character_id=charID)
		result = client.request(charLocation)
		location = json.loads(result.raw)
		sysID = location.get('solar_system_id')
		returnArray = [{"sysID": sysID}]
		return jsonify(results=returnArray)

@app.route('/')
def index():
	if 'token' in session:
		try:
			security.update_token(session['token'])
		except APIException as err:
			print err
			secure = security.get_auth_uri(scopes=scopes)
			return "<a href='"+secure+"'><img src='https://images.contentful.com/idjq7aai9ylm/4fSjj56uD6CYwYyus4KmES/4f6385c91e6de56274d99496e6adebab/EVE_SSO_Login_Buttons_Large_Black.png?w=270&h=45'></a>" 
		try:
			verify = security.verify()
		except:
			secure = security.get_auth_uri(scopes=scopes)
			return "<a href='"+secure+"'><img src='https://images.contentful.com/idjq7aai9ylm/4fSjj56uD6CYwYyus4KmES/4f6385c91e6de56274d99496e6adebab/EVE_SSO_Login_Buttons_Large_Black.png?w=270&h=45'></a>" 
		session['char'] = verify
		return render_template('index.html')
	else:
		secure = security.get_auth_uri(scopes=scopes)
		return "<a href='"+secure+"'><img src='https://images.contentful.com/idjq7aai9ylm/4fSjj56uD6CYwYyus4KmES/4f6385c91e6de56274d99496e6adebab/EVE_SSO_Login_Buttons_Large_Black.png?w=270&h=45'></a>" 


@app.route('/oauth')
def oauth():
	code = request.args.get('code')
	token = security.auth(code)
	session['token'] = token
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(
		host=serverIP,
		port=serverPort,
		debug=debug
		)