# -*- coding: utf-8 -*-

import sqlite3
import sys

db = sqlite3.connect("steam_data.db")
c = db.cursor()
c.execute('''CREATE TABLE steam_data
	(app_id INTEGER PRIMARY KEY, game_name TEXT, genre_1 TEXT, genre_2 TEXT, genre_3 TEXT, genre_4 TEXT, genre_5 TEXT, metacritic INTEGER, release_year INTEGER, developer TEXT, publisher TEXT, data_checked INTEGER)''')
db.commit()
db.close()