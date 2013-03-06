import urllib, urllib2, psycopg2, itertools

db = psycopg2.connect("user=postgres dbname=SteamCategorizer password='password'")
c = db.cursor()
c.execute("""SELECT app_id FROM steam_data;""")
app_list = c.fetchall()
app_list = list(app_list)
URL = "http://store.steampowered.com/app/"

def GetGenres(html_genre):
	genres = []

	# Cut HTML down to just Genres section
	genre_list_start = html_genre.find("Genre:")
	if genre_list_start == -1:
		return genres
	genre_list_end = html_genre.find("Release Date:", genre_list_start)

	html_genre = html_genre[genre_list_start:genre_list_end]

	while True:
		find_genre = html_genre.find('http://store.steampowered.com/genre')
		if find_genre == -1:
			break
		genre_start = html_genre.find('>', find_genre)
		genre_end = html_genre.find('</a>', genre_start)
		genre_name = html_genre[genre_start + 1:genre_end]
		genres.append(genre_name)

		html_genre = html_genre[genre_end:]

	return genres

def GetMetaScore(html):
	meta_score_start = html.find("game_area_metascore")
	if meta_score_start == -1:
		return ""
	meta_score_end = html.find("<", meta_score_start)
	meta_score = html[meta_score_start + 30: meta_score_end]
	return meta_score



def GetReleaseYear(html):
	release_date_start = html.find("<b>Release Date:")
	if release_date_start == -1:
		return ""
	release_year_end = html.find("<br>", release_date_start)
	release_year = html[release_year_end - 4: release_year_end]
	return release_year



def GetDevPub(html, devpub):
	find_text = "<b>{0}:</b>".format(devpub)
	devpub_section_start = html.find(find_text)
	if devpub_section_start == -1:
		return ""
	devpub_section_start = html.find("<a href", devpub_section_start)
	devpub_start = html.find('">', devpub_section_start)
	devpub_end = html.find("</a>", devpub_start)
	devpub_content = html[devpub_start + 2: devpub_end]
	return devpub_content



for app_id in reversed(app_list):
	c.execute("""SELECT genre_1 FROM steam_data WHERE app_id = %s AND genre_1 IS NOT NULL;""", [app_id])
	if c.fetchone() != None:
		app_list.remove(app_id)

for app_id in app_list:
	c.execute("""SELECT game_name FROM steam_data WHERE app_id = %s;""", [app_id])
	name = c.fetchone()
	app_id = str(app_id)
	app_id = app_id[1:len(app_id) - 2]
	html = ''

	# Get and read HTML
	while True:
		try:
			response = urllib2.urlopen(URL + str(app_id))
			# Check for and bypass agecheck
			if response.geturl() == ("http://store.steampowered.com/agecheck/app/" + str(app_id)):
				opener = urllib2.build_opener()
				opener.addheaders.append(('Cookie','birthtime=31564801'))
				opener.addheaders.append(('Cookie','lastagecheckage=1-January-1971'))
				response = opener.open(URL + str(app_id))
				html = response.read()
			# Check if app does not have store page
			elif response.geturl() == "http://store.steampowered.com/" or response.geturl() == "store.steampowered.com":
				break
			else:
				html = response.read()
		except urllib2.HTTPError, e:
			if e.getcode() == 500:
				continue
			else:
				print e.code
				print e.read()
				break
		break

	# Get genres
	genres = (GetGenres(html))
	metacritic = GetMetaScore(html)
	release_year = GetReleaseYear(html)
	developer = GetDevPub(html, "Developer")
	publisher = GetDevPub(html, "Publisher")

	print "Updating genres for " + str(name)[1:len(str(name))-2] + "."

	for genre, i in itertools.izip(genres,range(1,6)):
		sql_statement = """UPDATE steam_data SET genre_{0} = '{1}' WHERE app_id = {2};""".format(i, genres[i-1], app_id)
		c.execute(sql_statement)
	
	print "Finished updating genres for " + app_id + ".\n\n"

	if metacritic != "":
		c.execute("""UPDATE steam_data SET metacritic = %s WHERE app_id = %s""", (metacritic, app_id))

	if release_year != "":
		c.execute("""UPDATE steam_data SET release_year = %s WHERE app_id = %s""", (release_year, app_id))

	if developer != "":
		c.execute("""UPDATE steam_data SET developer = %s WHERE app_id = %s""", (developer, app_id))

	if publisher != "":
		c.execute("""UPDATE steam_data SET publisher = %s WHERE app_id = %s""", (publisher, app_id))


	db.commit()

db.close()

