
import get_steam_data
import wx, datetime, urllib2, sqlite3
db = sqlite3.connect("steam_data.db")
c = db.cursor()

get_steam_data.run(db,c)