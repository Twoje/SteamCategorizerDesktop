import os, wx, psycopg2, datetime, urllib2
import xml.etree.ElementTree as ET


class Start(wx.Frame):
	def __init__(self, parent, title):
		# Create window
		wx.Frame.__init__(self, parent, title = title, size=(1280, 1024), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

		self.InitUI()

	def InitUI(self):
		panel = wx.Panel(self)

		# Allow window to close on clicking X
		self.Bind(wx.EVT_CLOSE, self.CloseWindow)

		# FONT
		font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)


	###### MENUBAR ######
		# Create menubar and dropdowns
		menuBar = wx.MenuBar()

		# Add menubar dropdown
		fileMenu = wx.Menu()
		menuBar.Append(fileMenu, "File")
		
		# Import option
		fileItem1 = fileMenu.Append(wx.NewId(), "Import Steam File", "Steam/userdata/{user id}/7/remote/sharedconfig.vdf")
		self.Bind(wx.EVT_MENU, self.ImportFile, fileItem1)

		# Quit option
		fileItem2 = fileMenu.Append(wx.ID_EXIT, "Quit", "Close the program")
		self.Bind(wx.EVT_MENU, self.CloseWindow, fileItem2)

		# Draws the menubar
		self.SetMenuBar(menuBar)


	###### STATUS BAR ######
		self.StatusBar = self.CreateStatusBar()


	###### SEARCH BOX ######
		wx.StaticText(panel, -1, "Search:", pos=(10,15))
		self.Search = wx.TextCtrl(panel, -1, "", pos=(50, 10), size=(400,-1))
		self.Search.Enable(False)
		self.Search.Bind(wx.EVT_TEXT, self.SearchGames)


	###### GAME LIST ######
		wx.StaticText(panel, -1, "UNCATEGORIZED", pos=(10,40)).SetFont(font)
		self.Uncategorized = wx.ListBox(panel, -1, (10, 60), (440, 830), [], wx.LB_EXTENDED)
		self.Show(True)


	###### GENRE LIST ######
		self.Genres = wx.ListBox(panel, -1, (470, 60), (150, 500), [], wx.LB_SINGLE|wx.LB_SORT)
		self.Genres.Bind(wx.EVT_LISTBOX, self.GenreClick)


	###### SORT DROPDOWN ######
		wx.StaticText(panel, -1, "Sort:", pos=(300,40))
		self.SortOptions = wx.ComboBox(panel, -1, 
			pos=(330, 35), 
			size=(120, -1), 
			choices=['A to Z', 'Z to A', 'AppID Ascending', 'AppID Descending'], 
			style=wx.CB_READONLY)


	###### CATEGORIZATION OPTIONS ######
		self.CategoryOptions = wx.ComboBox(panel, -1, 
			pos=(470, 35), 
			size=(150, -1), 
			choices=['Genres', 'Metascore', 'Release Year', 'Developer', 'Publisher'], 
			style=wx.CB_READONLY)


	###### CATEGORIES LIST ######
		wx.StaticText(panel, -1, "CATEGORIES", pos=(640,40)).SetFont(font)
		self.Categories = wx.ListBox(panel, -1, (640, 60), (150, 500), [], wx.LB_SINGLE|wx.LB_SORT)
		self.Categories.Bind(wx.EVT_LISTBOX, self.CategoryClick)


	###### CATEGORY GAMES ######
		wx.StaticText(panel, -1, "CATEGORY GAMES", pos=(810,40)).SetFont(font)
		self.CategoryGames = wx.ListBox(panel, -1, pos=(810, 60), size=(440,830), style=wx.LB_EXTENDED)


	###### DELETED LIST ######
		wx.StaticText(panel, -1, "DELETED GAMES", pos=(470, 630)).SetFont(font)
		self.Delete = wx.ListBox(panel, -1, (470, 650), (320, 240), [], wx.LB_EXTENDED)

	###### BUTTONS ######
		# Import Button
		btnImport = wx.Button(panel, label="Import", pos=(470, 900), size=(60, 30))
		btnImport.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				'Import Steam Categories file (sharedconfig.vdf)'))
		btnImport.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.Bind(wx.EVT_BUTTON, self.ImportFile, btnImport)

		# Delete Button
		self.btnDelete = wx.Button(panel, label="Delete Game", pos=(600, 615), size=(90, 30))
		self.btnDelete.Enable(False)
		self.btnDelete.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				"Remove selected game(s) from Uncategorized. " +
				"Use this for stuff no longer in your library, e.g. deleted demos, free-weekend games, etc. "))
		self.btnDelete.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnDelete.Bind(wx.EVT_BUTTON, self.DeleteGame)

		# Add Back Button
		self.btnAddBack = wx.Button(panel, label="Add Back", pos=(700, 615), size=(90, 30))
		self.btnAddBack.Enable(False)
		self.btnAddBack.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				"Add games you might have accidentally removed."))
		self.btnAddBack.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnAddBack.Bind(wx.EVT_BUTTON, self.AddBack)

		# Clear Filter Button
		self.btnClearFilters = wx.Button(panel, label="Clear Filters", pos=(700, 900), size=(90, 30))
		self.btnClearFilters.Enable(False)
		self.btnClearFilters.Bind(wx.EVT_ENTER_WINDOW, lambda event: self.onMouseOver(event, 'Clear all filters.'))
		self.btnClearFilters.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnClearFilters.Bind(wx.EVT_BUTTON, self.ClearFilters)

		# Save Button
		self.btnSave = wx.Button(panel, label="Save", pos=(630, 900), size=(50, 30))
		self.btnSave.Enable(False)
		self.btnSave.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				'Save file with changes.'))
		self.btnSave.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnSave.Bind(wx.EVT_BUTTON, self.Save)

		# Backup Button
		self.btnBackup = wx.Button(panel, label="Backup", pos=(550, 900), size=(60, 30))
		self.btnBackup.Enable(False)
		utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M")
		self.btnBackup.Bind(wx.EVT_ENTER_WINDOW, lambda event: self.onMouseOver(event, 
			"""Backup imported file. This is HIGHLY RECOMMENDED. File will be saved as '{0}_backup_{1}'.""".format(self.filename, utc_datetime)))
		self.btnBackup.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.Bind(wx.EVT_BUTTON, self.BackUp, self.btnBackup)

		# Add to Category Button
		self.btnAddSelected = wx.Button(panel, label=">", pos=(470, 570), size=(60, 30))
		self.btnAddSelected.Enable(False)
		self.btnAddSelected.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				'Add selected games to current category.'))
		self.btnAddSelected.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnAddSelected.Bind(wx.EVT_BUTTON, self.AddSelected)

		# Remove from Category Button
		self.btnRemoveSelected = wx.Button(panel, label="<", pos=(730, 570), size=(60, 30))
		self.btnRemoveSelected.Enable(False)
		self.btnRemoveSelected.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				'Remove selected games from current category.'))
		self.btnRemoveSelected.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnRemoveSelected.Bind(wx.EVT_BUTTON, self.RemoveSelected)

		# Add Category
		self.btnAddCategory = wx.Button(panel, label="+", pos=(770, 35), size=(20, 20))
		self.btnAddCategory.Enable(False)
		self.btnAddCategory.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				'Add new category.'))
		self.btnAddCategory.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnAddCategory.Bind(wx.EVT_BUTTON, self.AddCategory)

		# Remove Category
		self.btnRemoveCategory = wx.Button(panel, label="-", pos=(745, 35), size=(20, 20))
		self.btnRemoveCategory.Enable(False)
		self.btnRemoveCategory.Bind(
			wx.EVT_ENTER_WINDOW,
			lambda event: self.onMouseOver(
				event,
				'Remove selected category.'))
		self.btnRemoveCategory.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
		self.btnRemoveCategory.Bind(wx.EVT_BUTTON, self.RemoveCategory)


	def RefreshFilters(self, event):
		self.GetGenres()
		self.SearchFilter()
		self.FilterCategories()


	def Save(self, event):
		warning = wx.MessageDialog(self,
			'WARNING! This will overwrite the file that you imported! Click the Backup button to back up your file.',
			'WARNING!',
			wx.OK|wx.CANCEL)
		if warning.ShowModal() == wx.ID_OK:
			if self.file_loaded:
				self.SaveToFile()
			else:
				self.SaveNewFile()
		

	def SaveNewFile(self):
		file_content = """"UserRoamingConfigStore"
{
"Software"
	{
		"Valve"
		{
			"Steam"
			{
				"DesktopShortcutCheck"		"0"
				"StartMenuShortcutCheck"		"0"
				"AutoLaunchGameListCheck"		"0"
				"SteamDefaultDialog"		"#app_store"
				"SSAVersion"		"2"
				"apps"
				{\n"""

		for app_id in self.lstUncategorized:
			file_content = file_content + """					\"""" + app_id + """\"
					{
					}\n"""

		for app_id in self.lstCategories.keys():
			file_content = file_content + """					\"""" + app_id + """\"
					{0}
						"tags"
						{0}
							"{1}"		\"""".format("{", "0") + self.lstCategories[app_id] + """\"
						}
					}\n""" # Could add a 'favorites' to the app, so .format(favorite) where favorite = "0" or "1"


		file_content = file_content + """				}
				"PrivacyPolicyVersion"		"2"
			}
		}
	}
}"""

		file_dialog = wx.FileDialog(
			self,
			message="Save in Steam/userdata/{user id}/7/remote/",
			wildcard='sharedconfig.vdf',
			style=wx.SAVE)
		if file_dialog.ShowModal() == wx.ID_OK:
			file_path = file_dialog.GetDirectory()
			file_name = file_dialog.GetFilename()
		else:
			return 0

		self.SaveFile(file_content, file_path, file_name)


	def SaveToFile(self):
		file_read = open(os.path.join(self.dirname, self.full_filename), 'r')
		file_content = file_read.read()
		file_read.close()

		for app_id in self.lstUncategorized:
			app_loc = file_content.find("\n\t\t\t\t\t\"" + app_id + '"')
			if app_loc != -1:
				app_end = file_content.find("\n\t\t\t\t\t}", app_loc) # Use this to prevent unintended deletion if app doesn't have 'tags' in the vdf
				tags_loc_start = file_content.find('\n\t\t\t\t\t\t"tags"', app_loc, app_end)
				if tags_loc_start != -1:
					tags_loc_end = file_content.find("\n\t\t\t\t\t\t}", tags_loc_start)
					file_content = file_content[:tags_loc_start] + file_content[tags_loc_end + 8:]

		for app_id in self.lstCategories.keys():
			app_loc = file_content.find('\n\t\t\t\t\t"' + app_id + '"')
			if app_loc != -1:
				app_end = file_content.find("\n\t\t\t\t\t}", app_loc) # Use this to prevent unintended deletion if app doesn't have 'tags' in the vdf
				category_loc_start = file_content.find("\n\t\t\t\t\t\t\t\"", app_loc, app_end)
				if category_loc_start != -1:
					category_loc_start += 14 # Number of characters before actual category starts
					category_loc_end = file_content.find("\"", category_loc_start + 1)
					file_content = file_content[:category_loc_start] + self.lstCategories[app_id] + file_content[category_loc_end:]
				else:
					category_loc_start = file_content.find("{", app_loc)
					category_string = """
						"tags"
						{0}
							"{1}"		"{2}"
						{3}""".format("{", "0", self.lstCategories[app_id], "}")
					file_content = file_content[:category_loc_start] + category_string + file_content[category_loc_start + 1:]

			# Else add app_id

		file_dialog = wx.FileDialog(
			self,
			message="Save in Steam/userdata/{user id}/7/remote/",
			wildcard='*.vdf',
			style=wx.SAVE)
		if file_dialog.ShowModal() == wx.ID_OK:
			file_path = file_dialog.GetDirectory()
			file_name = file_dialog.GetFilename()
		else:
			return 0

		self.SaveFile(file_content, file_path, file_name)


	def SaveFile(self, file_content, file_path, file_name):
		file_write = open(os.path.join(file_path, file_name), 'w')
		file_write.write(file_content)
		file_write.close()

	def AddCategory(self, event):
		new_category_dialog = wx.TextEntryDialog(self, message="Please enter the new category here:", style=wx.OK|wx.CANCEL)
		if new_category_dialog.ShowModal() == wx.ID_OK:
			new_category = new_category_dialog.GetValue()
			if new_category != '' and new_category not in self.Categories.GetStrings():
				self.Categories.Append(new_category)

		new_category_dialog.Destroy()


	def RemoveCategory(self, event):
		warning = wx.MessageDialog(self, 'WARNING!\nThis will move all games from this category to Uncategorized!', 'WARNING!', wx.OK|wx.CANCEL)
		if warning.ShowModal() == wx.ID_OK:
			if self.Categories.GetSelection() == -1:
				return 0
			category = self.Categories.GetString(self.Categories.GetSelection())
			self.Categories.Delete(self.Categories.GetSelection())
			for app_id in self.lstCategories.keys():
				if self.lstCategories[app_id] == category:
					self.lstUncategorized.append(app_id)
					del self.lstCategories[app_id]
			self.CategoryGames.Clear()
			if self.Categories.GetCount() != 0:
				self.Categories.Select(0)
			self.RefreshFilters(event)


	def AddSelected(self, event):
		if self.Uncategorized.GetSelections() == -1 or  self.Categories.GetSelection() == -1:
			return 0
		category = self.Categories.GetString(self.Categories.GetSelection())
		selectionIDs = self.Uncategorized.GetSelections()
		for selectionID in reversed(selectionIDs):
			selection = self.Uncategorized.GetString(selectionID)
			app_id = selection[:selection.find(' -')]
			self.Uncategorized.Delete(selectionID)
			self.lstUncategorized.remove(app_id)
			self.lstCategories[app_id] = category

		if self.Uncategorized.GetCount() == 0:
			self.Genres.DeselectAll()

		self.RefreshFilters(event)


	def RemoveSelected(self, event):
		if self.CategoryGames.GetSelections() == -1:
			return 0

		selectionIDs = self.CategoryGames.GetSelections()
		for selectionID in reversed(selectionIDs):
			selection = self.CategoryGames.GetString(selectionID)
			app_id = selection[:selection.find(' -')]
			self.lstUncategorized.append(app_id)
			del self.lstCategories[app_id]

		self.RefreshFilters(event)



	def BackUp(self, event):
		utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M")
		file_to_backup = open(os.path.join(self.dirname, self.full_filename), 'r')
		file_data = file_to_backup.read()
		backup_file = open(os.path.join(self.dirname, "%s_backup_%s.vdf" % (self.filename, utc_datetime)), 'w')
		backup_file.write(file_data)
		file_to_backup.close()
		backup_file.close()
		wx.MessageBox('Backup has completed.', 'Success!', wx.OK)


	def onMouseOver(self, event, text):
		self.StatusBar.SetStatusText(text)


	def onMouseLeave(self, event):
		self.StatusBar.SetStatusText("")


	def ClearFilters(self, event):
		self.Search.Clear()
		self.Genres.DeselectAll()
		self.Uncategorized.Clear()
		for app_id in self.lstUncategorized:
			self.Uncategorized.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])


	def AddBack(self, event):
		if self.Delete.GetSelections() == -1:
			return 0
		selectionIDs = self.Delete.GetSelections()
		for selectionID in reversed(selectionIDs):
			selection = self.Delete.GetString(selectionID)
			app_id = selection[:selection.find(' -')]
			self.lstAppID.append(app_id)
			self.lstUncategorized.append(app_id)
			self.lstDelete.remove(app_id)
		self.Delete.Clear()
		for app_id in self.lstDelete:
			self.Delete.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])

		self.RefreshFilters(event)


	def DeleteGame(self, event):
		if self.Uncategorized.GetSelections() == -1:
			return 0
		selectionIDs = self.Uncategorized.GetSelections()
		for selectionID in reversed(selectionIDs):
			selection = self.Uncategorized.GetString(selectionID)
			app_id = selection[:selection.find(' -')]
			self.lstAppID.remove(app_id)
			self.lstUncategorized.remove(app_id)
			self.lstDelete.append(app_id)
			self.Delete.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])
			self.Uncategorized.Delete(selectionID)

		if self.Uncategorized.GetCount() == 0:
			self.Genres.DeselectAll()

		# if self.Genres.GetSelection() != -1 and not self.Uncategorized.GetStrings():
		# 	self.Genres.Delete(self.Genres.GetSelection())

		self.RefreshFilters(event)


	def CategoryClick(self, event):
		self.FilterCategories()


	def FilterCategories(self):
		categoryID = self.Categories.GetSelection()
		if categoryID == -1:
			return 0
		category = self.Categories.GetString(categoryID)
		self.CategoryGames.Clear()
		for app_id in self.lstCategories:
			if self.lstCategories[str(app_id)] == category:
				self.CategoryGames.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])


	# Get Genres for all Uncategorized
	def GetGenres(self):
		selected_genre = ''
		if self.Genres.GetSelection() != -1:
			selected_genre = self.Genres.GetString(self.Genres.GetSelection())

		self.Genres.Clear()

		genres = []

		for app_id in self.lstUncategorized:
			for i in range(0, 5):
				sql_statement = """SELECT genre_{0} FROM steam_data WHERE app_id = {1} AND genre_{0} IS NOT NULL;""".format(i + 1, app_id)
				c.execute(sql_statement)
				# Move to next app_id if genre_{0} is null
				if c.rowcount == 0:
					break
				# Add genre to list if nonexistant
				genre = str(c.fetchone())
				genre = genre[2:len(genre)-3]
				if genre not in genres:
					genres.append(genre)

		# Append genres to Genres listbox
		for genre in genres:
			self.Genres.Append(genre)

		if selected_genre != -1:
			for location in range(self.Genres.GetCount()):
				if self.Genres.GetString(location) == selected_genre:
					self.Genres.SetSelection(location)


	def GenreClick(self, event):
		genreID = self.Genres.GetSelection()
		if genreID != -1:
			genre = self.Genres.GetString(genreID)
			self.Uncategorized.Clear()
			#genres = self.Genres.GetStrings()
			for app_id in self.lstUncategorized:
				for i in range(0, 5):
					sql_statement = """SELECT genre_{0} FROM steam_data WHERE app_id = {1} AND genre_{0} IS NOT NULL;""".format(i + 1, app_id)
					c.execute(sql_statement)
					# Move to next app_id if genre_{0} is null
					if c.rowcount == 0:
						break
					app_genre = str(c.fetchone())
					app_genre = app_genre[2:len(app_genre)-3]
					if app_genre == genre:
						self.Uncategorized.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])

		self.SearchFilter()


	def SearchGames(self, event):
		if self.Genres.GetSelection() != -1:
			self.GenreClick(event)
		else:
			self.Uncategorized.Clear()
			for app_id in self.lstUncategorized:
				self.Uncategorized.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])
		event.Skip()
		
		self.RefreshFilters(event)


	# Filter based on searchbox text
	def SearchFilter(self):
		txtValue = self.Search.GetValue()
		selection = self.Search.GetSelection()
		self.Search.SetSelection(*selection)

		# Edit listbox to show only games containing search box
		current_app_ids = []
		if self.Genres.GetSelection() == -1:
			for item in self.lstUncategorized:
				current_app_ids.append(item)
		else:
			for item in self.Uncategorized.GetStrings():
				current_app_ids.append(item[:item.find(' -')])
		self.Uncategorized.Clear()
		for app_id in current_app_ids:
			if self.lstGames[str(app_id)].upper().find(txtValue.upper()) != -1:
				self.Uncategorized.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])



	# Close function
	def CloseWindow(self, event):
		db.close()
		self.Destroy()


	def GetUserXml(self, steam_id):
		URL = "http://steamcommunity.com/id/{0}/games?tab=all&xml=1".format(steam_id)
		html = ''
		user_xml = ''
		try:
			response = urllib2.urlopen(URL)
			html = response.read()
			if html.find("The specified profile could not be found.") != -1:
				return 0
		except urllib2.HTTPError, e:
			if e.getcode() == 503:
				user_xml = self.GetUserXml(steam_id)
			else:
				return 0
		if user_xml == '':				
			user_xml = ET.fromstring(html)

		return user_xml

	def GetUserAppGames(self, steam_id):
		app_games = {}

		user_xml = self.GetUserXml(steam_id)
		
		self.loading_dialog.Update(2)

		if user_xml == 0:
			return 0

		for game in user_xml.iter('game'):
			xml_name = game.find('name').text
			app_id = game.find('appID').text
			app_games[app_id] = xml_name
		return app_games

	def GetUserAppIDs(self, steam_id):
		app_ids = []

		user_xml = self.GetUserXml(steam_id)

		self.loading_dialog.Update(7)

		if user_xml == 0:
			return 0

		for game in user_xml.iter('game'):
			xml_name = game.find('appID').text
			app_ids.append(xml_name)

		return app_ids


	# Import file function
	def ImportFile(self, event):
		get_steam_id = wx.TextEntryDialog(self, message="Please enter the your Steam ID here:", style=wx.OK|wx.CANCEL)
		if get_steam_id.ShowModal() == wx.ID_OK:
			steam_id = get_steam_id.GetValue()
		else:
			return 0
		get_steam_id.Destroy()

		self.Uncategorized.Clear()
		self.Genres.Clear()
		self.Categories.Clear()
		self.CategoryGames.Clear()
		self.Delete.Clear()

		self.lstCategories = {}
		self.lstUncategorized = []
		self.lstDelete = []

		self.loading_dialog = wx.ProgressDialog("Loading", "Please wait. Loading Steam ID.", maximum=10, style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH)

		self.lstGames = self.GetUserAppGames(steam_id)
		self.loading_dialog.Update(5)
		self.lstAppID = self.GetUserAppIDs(steam_id)
		self.loading_dialog.Update(10)

		self.loading_dialog.Destroy()

		if self.lstGames == 0 or self.lstAppID == 0:
			wx.MessageBox('Steam ID loading failed. Please make sure your Steam profile is set to Public.', 'Oops!', wx.OK)
			return 0

		load_success = wx.MessageDialog(
			self,
			"Load successful!\n"
			"Find your sharedconfig.vdf file. It should be located in:\n"
			"Steam/userdata/{user id}/7/remote/\n"
			"Click Cancel if you don't want to load a file.",
			'Load File',
			wx.OK|wx.CANCEL)
		self.file_loaded = False
		if load_success.ShowModal() == wx.ID_OK:
			fileDialog = wx.FileDialog(self, "Choose your .vdf file", '', '', 'sharedconfig.vdf', wx.OPEN)
			if fileDialog.ShowModal() == wx.ID_OK:
				self.full_filename = fileDialog.GetFilename()
				self.filename = os.path.splitext(self.full_filename)[0]
				self.dirname = fileDialog.GetDirectory()
				steam_file = open(os.path.join(self.dirname, self.full_filename), 'r')
				file_content = steam_file.read()
				steam_file.close()
				self.file_loaded = True
			fileDialog.Destroy()
		else:
			for app_id in self.lstAppID:
				self.Uncategorized.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])
				self.lstUncategorized.append(app_id)
			self.EnableAll()
			self.btnBackup.Enable(False)
			self.GetDatabaseInfo(event)
			return 0

		self.GetCategories(file_content)
		self.GetDatabaseInfo(event)
		self.EnableAll()


	def GetDatabaseInfo(self, event):
		self.GetGenres()
		self.ClearFilters(event)
		

	def EnableAll(self):
		self.Search.Enable(True)
		self.btnClearFilters.Enable(True)
		self.btnBackup.Enable(True)
		self.btnDelete.Enable(True)
		self.btnAddBack.Enable(True)
		self.btnSave.Enable(True)
		self.btnAddCategory.Enable(True)
		self.btnRemoveCategory.Enable(True)
		self.btnAddSelected.Enable(True)
		self.btnRemoveSelected.Enable(True)


	def GetFileApps(self, file_content):
		content_done = ''
		file_apps = []

		while True:
			app_start = file_content.find('\n\t\t\t\t\t"', len(content_done))
			if app_start == -1:
				break
			app_start += 7
			app_end = file_content.find('"', app_start)
			app_id = file_content[app_start: app_end]

			content_done = content_done + file_content[len(content_done): app_end]

			file_apps.append(app_id)

		for app_id in file_apps:
			if app_id not in self.lstAppID:
				sql_statement = """SELECT game_name FROM steam_data WHERE app_id = {0};""".format(app_id)
				c.execute(sql_statement)
				if c.description == None:
					continue
				game_name = str(c.fetchone())
				game_name = game_name[3:len(game_name)-3]
				game_name = game_name.encode('utf8')
				self.lstAppID.append(app_id)
				self.lstGames[str(app_id)] = game_name




	def GetCategories(self, file_content):

		self.GetFileApps(file_content)

		for app_id in self.lstAppID:
			app_start = file_content.find('\n\t\t\t\t\t"{0}"'.format(app_id))
			if app_start == -1:
				continue
			app_start = app_start + 7
			app_end = file_content.find('"', app_start)

			app_section_start = file_content.find('\n\t\t\t\t\t{', app_end)
			app_section_end = file_content.find('\n\t\t\t\t\t}', app_section_start)
			app_section = file_content[app_section_start: app_section_end]

			category = ''
			category_start = app_section.find('\n\t\t\t\t\t\t{')
			if category_start != -1:
				category_start = app_section.find('"', category_start) + 6
				category_end = app_section.find('"', category_start)
				category = app_section[category_start: category_end]

			app_name = self.lstGames[str(app_id)]
			app_name = app_name[2:len(app_name)-3]
			app_name = app_name

			if category != '':
				self.lstCategories[app_id] = category
			else:
				self.Uncategorized.Append(str(app_id) + ' - ' + self.lstGames[str(app_id)])
				self.lstUncategorized.append(app_id)


		self.lstAppID.sort()
		for app_id, category in self.lstCategories.iteritems():
			if category not in self.Categories.GetStrings():
				self.Categories.Append(category)

		self.Categories.Select(0)
		self.FilterCategories()
		



if __name__ == '__main__':
	# Start database
	db = psycopg2.connect("user=postgres dbname=SteamCategorizer password='password'")
	c = db.cursor()

	# Create the window
	app = wx.App()
	frame = Start(None, title="Steam Categorizer")
	app.MainLoop()
