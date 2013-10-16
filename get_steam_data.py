import urllib, urllib2, itertools


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


def run(db, c):
	c.execute("""SELECT app_id FROM steam_data;""")
	app_list_tuple = c.fetchall()
	app_list = []
	for i in app_list_tuple:
		app_list.append(i[0])

	for app_id in reversed(app_list):
		c.execute("""SELECT app_id FROM steam_data WHERE app_id = ? AND data_checked=1;""", [app_id])
		if c.fetchone() != None:
			app_list.remove(app_id)

	for app_id in app_list:
		c.execute("""SELECT game_name FROM steam_data WHERE app_id = ?;""", [app_id])
		name = c.fetchone()[0]
		html = ''

		# Get and read HTML
		while True:
			try:
				response = urllib2.urlopen(URL + str(app_id))
				# Check for and bypass agecheck
				if response.geturl().find("http://store.steampowered.com/agecheck/app/" + str(app_id)) != -1:
					opener = urllib2.build_opener()
					opener.addheaders.append(('Cookie','birthtime=31564801'))
					opener.addheaders.append(('Cookie','lastagecheckage=1-January-1971'))
					response = opener.open(URL + str(app_id))
					html = response.read()
				# Check if app does not have store page
				elif response.geturl() == "http://store.steampowered.com/" or response.geturl() == "http://store.steampowered.com":
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

		# Causing UnicodeError
		#print "Updating data for {0}.".format(name.encode('utf8'))
		print "Updating data for game."

		for genre, i in itertools.izip(genres,range(1,6)):
			sql_statement = """UPDATE steam_data SET genre_{0} = '{1}' WHERE app_id = {2};""".format(i, genres[i-1], app_id)
			c.execute(sql_statement)
		
		if metacritic != "":
			c.execute("""UPDATE steam_data SET metacritic = ? WHERE app_id = ?""", (metacritic, app_id))

		if release_year != "":
			c.execute("""UPDATE steam_data SET release_year = ? WHERE app_id = ?""", (release_year, app_id))

		if developer != "":
			c.execute("""UPDATE steam_data SET developer = ? WHERE app_id = ?""", (developer.decode('utf8'), app_id))

		if publisher != "":
			c.execute("""UPDATE steam_data SET publisher = ? WHERE app_id = ?""", (publisher.decode('utf8'), app_id))

		c.execute("""UPDATE steam_data SET data_checked = ? WHERE app_id = ?""", (1, app_id))

		print "Finished updating data for " + str(app_id) + ".\n\n"

		db.commit()

	db.close()


