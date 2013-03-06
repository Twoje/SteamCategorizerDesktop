import urllib2, xml.etree.ElementTree as ET, psycopg2

db = psycopg2.connect("user=postgres dbname=SteamCategorizer password='password'")
c = db.cursor()

url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=xml"


response = urllib2.urlopen(url)
html = response.read()

steam = ET.fromstring(html)

for app in steam.iter('app'):
	xml_name = app.find('name').text
	app_id = app.find('appid').text
	if xml_name == None:
		continue
	game_name = xml_name.encode('ascii', 'replace')

	# Check if app already in DB
	c.execute("""SELECT game_name FROM steam_data WHERE app_id = %s;""", [app_id])
	if c.rowcount == 0:
		c.execute("""INSERT INTO steam_data (app_id, game_name) VALUES (%s, %s);""", (app_id, xml_name))
		db.commit()
		print "Added " + str(app_id) + " - " + game_name
	else:
		c.execute("""UPDATE steam_data SET game_name = %s WHERE app_id = %s;""", (xml_name, app_id))
		db.commit()
