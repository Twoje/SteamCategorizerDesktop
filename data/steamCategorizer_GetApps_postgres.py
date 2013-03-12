# -*- coding: utf-8 -*-
import urllib2, xml.etree.ElementTree as ET
import wx
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

db = psycopg2.connect("user=postgres dbname=SteamCategorizer password='password'")
c = db.cursor()

url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=xml"


response = urllib2.urlopen(url)
html = response.read()

steam = ET.fromstring(html)

def run(c):
	for app in steam.iter('app'):
		xml_name = app.find('name').text
		app_id = app.find('appid').text
		if xml_name == None:
			continue

		# Check if app already in DB
		c.execute("""SELECT game_name FROM steam_data WHERE app_id = %s;""", [app_id])
		if c.rowcount == 0:
			c.execute("""INSERT INTO steam_data (app_id, game_name) VALUES (%s, %s);""", (app_id, xml_name))
			db.commit()
		else:
			game_name = c.fetchone()[0]
			if game_name == xml_name:
				continue
			else:
				c.execute("""UPDATE steam_data SET game_name = %s, data_checked = %s WHERE app_id = %s;""", (xml_name, "FALSE", app_id))
				print "Updated {0} to {1}".format(game_name, xml_name)
				db.commit()

run(c)