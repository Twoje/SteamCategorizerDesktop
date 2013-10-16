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
		if xml_name == None:
			continue
		xml_name.encode('utf-8')
		app_id = app.find('appid').text

		# Check if app already in DB
		c.execute("""SELECT game_name FROM steam_data WHERE app_id = ?;""", [app_id])
		game_name = c.fetchone()
		if game_name is None:
			c.execute("""INSERT INTO steam_data (app_id, game_name) VALUES (?, ?);""", (app_id, xml_name))
			db.commit()
			# Causing UnicodeError
			#print "Added {0} - {1}".format(app_id, xml_name.encode('latin-1'))
			print "Added a new game."
		else:
			game_name = game_name[0]
			if game_name == xml_name:
				continue
			else:
				c.execute("""UPDATE steam_data SET game_name = ?, data_checked = ? WHERE app_id = ?;""", (xml_name, 0, app_id))
				db.commit()
				# Causing UnicodeError
				#print "Finished updating {0} - {1}".format(app_id, game_name.encode('latin-1'))
				print "Finished updating game."
