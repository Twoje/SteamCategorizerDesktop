# -*- coding: utf-8 -*-

import sys
import urllib2, xml.etree.ElementTree as ET


url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=xml"


response = urllib2.urlopen(url)
html = response.read()

steam = ET.fromstring(html)

def run(db, c):
	for app in steam.iter('app'):
		xml_name = app.find('name').text
		app_id = app.find('appid').text
		if xml_name == None:
			continue

		# Check if app already in DB
		c.execute("""SELECT game_name FROM steam_data WHERE app_id = ?;""", [app_id])
		game_name = c.fetchone()[0]
		xml_name.encode('utf-8')
		if game_name == None:
			c.execute("""INSERT INTO steam_data (app_id, game_name) VALUES (?, ?);""", (app_id, xml_name))
			db.commit()
			print "Added {0} - {1}".format(app_id, xml_name.encode('utf8'))
		else:
			if game_name == xml_name:
				continue
			else:
				c.execute("""UPDATE steam_data SET game_name = ?, data_checked = ? WHERE app_id = ?;""", (xml_name, 0, app_id))
				db.commit()
				print "Finished updating {0} - {1}".format(app_id, game_name.encode('utf8'))
