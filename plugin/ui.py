from os.path import exists
from time import time, perf_counter

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.EpgList import EPGList, EPG_TYPE_SINGLE, Rect
from Components.Sources.StaticText import StaticText
from Components.config import config
from Screens.EpgSelection import EPGSelection
from Screens.MessageBox import MessageBox
from Tools.Directories import SCOPE_CONFIG, resolveFilename
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont

from skin import applySkinFactor, parseScale

from . import _
from .configuration import cfg
from .epgdata import collect_events, event_key, selection_index, sort_events
from .services import CustomEPGServiceEditor, service_name
from .storage import load_legacy_services, load_services

VERSION = "0.6"

class CustomEPGList(EPGList):
	"""SingleEPG rows with an additional service column and a shared event list."""
	def __init__(self, selChangedCB, timer):
		EPGList.__init__(self, type=EPG_TYPE_SINGLE, selChangedCB=selChangedCB, timer=timer)
		self.list = []
		self.all_events = []
		self.service_names = {}
		self.minimum_duration = int(cfg.minimum_duration.value)

	# Default dimensions use OpenPLi's 720p skin factor. Skin overrides use parseScale.
	columnDefaults = {
		"customWeekdayWidth": 40,
		"customDayDateGap": 12,
		"customDateTimeWidth": 96,
		"customDateEventGap": 8,
		"customEventServiceGap": 10,
		"customServiceWidth": 130,
		"customServiceRatingGap": 0,
		"customRatingWidth": 24,
	}

	def applySkin(self, desktop, parent):
		self.columnDimensions = {}
		remaining = []
		for name, value in self.skinAttributes or []:
			if name in self.columnDefaults:
				try:
					self.columnDimensions[name] = max(0, parseScale(value))
				except (TypeError, ValueError):
					print("[CustomEPG] Invalid skin attribute %s: %s" % (name, value))
			else:
				remaining.append((name, value))
		self.skinAttributes = remaining
		result = EPGList.applySkin(self, desktop, parent)
		self.l.setFont(2, gFont(self.eventTimeFont.family, self.eventTimeFont.pointSize + 4))
		self.l.setFont(3, gFont(self.eventTimeFont.family, self.eventTimeFont.pointSize + 2))
		return result

	def recalcEntrySize(self):
		EPGList.recalcEntrySize(self)
		dimensions = {name: applySkinFactor(value) for name, value in self.columnDefaults.items()}
		dimensions.update(getattr(self, "columnDimensions", {}))
		size = self.l.getItemSize()
		width, height = max(0, size.width() - self.sidesMargin), size.height()
		# Allocate the fixed columns from either edge; the event takes the remainder.
		day_width = min(width, dimensions["customWeekdayWidth"])
		date_x = min(width, day_width + dimensions["customDayDateGap"])
		date_width = min(width - date_x, dimensions["customDateTimeWidth"])
		event_x = min(width, date_x + date_width + dimensions["customDateEventGap"])
		rating_width = min(width - event_x, dimensions["customRatingWidth"]) if self.sorting == 2 else 0
		rating_x = width - rating_width
		service_end = max(event_x, rating_x - dimensions["customServiceRatingGap"]) if self.sorting == 2 else width
		service_width = min(service_end - event_x, dimensions["customServiceWidth"])
		service_x = service_end - service_width
		event_width = max(0, service_x - dimensions["customEventServiceGap"] - event_x)
		self.weekday_rect = Rect(0, 0, day_width, height)
		self.datetime_rect = Rect(date_x, 0, date_width, height)
		self.descr_rect = Rect(event_x, 0, event_width, height)
		self.service_rect = Rect(service_x, 0, service_width, height)
		self.rating_rect = Rect(rating_x, 0, rating_width, height)

	def buildSingleEntry(self, service, eventId, beginTime, duration, title):
		row = EPGList.buildSingleEntry(self, service, eventId, beginTime, duration, title)
		ended = beginTime is not None and duration is not None and beginTime + duration <= time()
		# SingleEPG offsets the event text after timer icons but keeps its full
		# width. Clip it to our narrower event column so it cannot cover the
		# service or rating columns.
		for index, entry in enumerate(row[1:], 1):
			if entry[0] == eListboxPythonMultiContent.TYPE_TEXT:
				entry = list(entry)
				# Keep secondary columns small; enlarge only the event title.
				entry[5] = 3 if index in (1, 2) else 1
				if index == 2:  # Date/time, immediately after the weekday.
					entry[6] = RT_HALIGN_LEFT | RT_VALIGN_CENTER
				if entry[7] == title and self.descr_rect.x <= entry[1] < self.service_rect.x:
					entry[5] = 2
					entry[3] = max(0, self.descr_rect.x + self.sidesMargin + self.descr_rect.w - entry[1])
					if ended: # finished events
						entry.extend([None] * max(0, 10 - len(entry)))
						entry[8] = 0x00777777
						entry[9] = None
				if index in (1, 2):		# day, date/time
					entry.extend([None] * max(0, 10 - len(entry)))
					entry[8] = 0x00d0d0d0	# row: gray
					entry[9] = None		# selected row: color from skin
				elif (self.sorting == 2 and entry[1] == self.rating_rect.x + self.sidesMargin):	# rating
					entry.extend([None] * max(0, 10 - len(entry)))
					entry[8] = 0x000080b0	# rating: blue light
					entry[9] = None		# selected row: color from skin
				row[index] = tuple(entry)
		r = self.service_rect
		row.append((eListboxPythonMultiContent.TYPE_TEXT, r.x + self.sidesMargin, r.y, r.w, r.h, 1, RT_HALIGN_LEFT | RT_VALIGN_CENTER, self.service_names.get(service, "<N/A>"),0x00d0d0d0, None)) # service
		return row

	def reload(self, references, sorting=0, filtering=0):
		selected = event_key(self.l.getCurrentSelection())
		now = int(time())
		begin = now - int(config.epg.histminutes.value) * 60
		self.all_events = collect_events(self.queryEPG, references, begin)
		self.service_names = {ref: service_name(ref) or "<N/A>" for ref in {row[0] for row in self.all_events}}
		self.applyView(sorting, filtering, selected=selected, now=now if not sorting else None)

	def applyView(self, sorting, filtering, selected=None, now=None):
		self.sorting = sorting
		rows = self.filtering_epg(self.all_events, filtering) if filtering else self.all_events
		if cfg.hide_started.value:
			current_time = int(time())
			rows = [row for row in rows if row[2] is not None and row[2] >= current_time]
		if self.minimum_duration:
			minimum_seconds = self.minimum_duration * 60
			rows = [row for row in rows if row[3] is not None and row[3] >= minimum_seconds]
		self.list = self.sortEvents(rows, sorting)
		self.l.setList(self.list)
		self.recalcEntrySize()
		if self.instance is not None and self.list:
			self.instance.moveSelectionTo(selection_index(self.list, selected, now))
		self.selectionChanged()

	def sortEvents(self, rows, sorting):
		if sorting != 1:
			return sort_events(rows, sorting, self.getEventRating)
		start = perf_counter()
		result = sort_events(rows, sorting, self.getEventRating, cfg.alphabetsort.value)
		print("[CustomEPG] A-Z sort (%s): %d events, %.1f ms" %
			(cfg.alphabetsort.value, len(rows), (perf_counter() - start) * 1000))
		return result

	def sortSingleEPG(self, sorting):
		# OpenPLi's moveToEventId alone cannot identify a row across multiple services.
		selected = event_key(self.l.getCurrentSelection())
		self.sorting = sorting
		self.list = self.sortEvents(self.list, sorting)
		self.recalcEntrySize()
		self.l.setList(self.list)
		if self.instance is not None and self.list:
			self.instance.moveSelectionTo(selection_index(self.list, selected))
		self.selectionChanged()


class CustomEPGSelection(EPGSelection):

	def __init__(self, session):
		self.custom_ready = False
		self.settings_error = None
		self.references = []
		# A string selects SingleEPG mode. No dependency on a currently playing service.
		EPGSelection.__init__(self, session, "")
		# EPGSearch injects an EPGSelectActions map at priority -1 into
		# EPGSelection.__init__. Keep our service editor on BLUE at priority -2.
		self["customEPGActions"] = ActionMap(["EPGSelectActions"], {
			"blue": self.blueButtonPressed,
		}, -2)
		self["durationFilterActions"] = HelpableActionMap(self, "NumberActions", {
			"5": (self.openDurationFilter, _("Filter by minimum event duration")),
		}, -2)
		self.skinName = ["CustomEPGSelection", "EPGSelection"]
		self["status"] = StaticText()
		self["list"] = CustomEPGList(self.onSelectionChanged, session.nav.RecordTimer)
		self["key_blue"].setText(_("Services"))
		self["key_red"].setText(_("Zap"))
		self.custom_ready = True
		self.onShown.append(self.refreshTimerIcons)
		# FallbackTimerList can defer onCreate until remote timers arrive.
		# Always populate at layout time as well; never fill an uncreated widget.
		if self.onCreate not in self.onLayoutFinish:
			self.onLayoutFinish.append(self.onCreate)

	def onCreate(self):
		if not self.custom_ready or self["list"].instance is None:
			return
		self.reloadEPG()

	def reloadEPG(self):
		try:
			path = resolveFilename(SCOPE_CONFIG, "customepg.xml")
			services = load_services(path) if exists(path) else load_legacy_services(resolveFilename(SCOPE_CONFIG, "customepg.json"))
		except (OSError, ValueError) as error:
			self.references = []
			self["list"].reload([], self.sort_type, self.filtering)
			self.settings_error = str(error)
			self.updateTitle()
			self.session.open(MessageBox, _("Cannot load CustomEPG settings:\n%s") % error, MessageBox.TYPE_ERROR)
			return
		self.settings_error = None
		self.references = [ref for ref, name in services]
		self["list"].reload(self.references, self.sort_type, self.filtering)
		self.updateTitle()
		self.refreshPartnerboxIcons()

	def refreshPartnerboxIcons(self):
		# Partnerbox patches EPGList's renderer, but our onCreate replaces its
		# timer-list fetch. Fetch via its own API, without SingleEPG's one-service
		# filter. Its async callback invalidates the list when timers arrive.
		fetch = getattr(self, "GetPartnerboxTimerlist", None)
		if callable(fetch):
			if not hasattr(self, "partnerboxentry"):
				self.PartnerboxInit(False)
			self.filterRef = False
			fetch()

	def updateTitle(self):
		title = "CustomEPG - " + (_("by time"), "A-Z", _("by rating"))[self.sort_type]
		if self.filtering:
			title += " " + self.getTimespanText()
		self.setTitle(title)
		if self.settings_error:
			status = _("Cannot load CustomEPG settings.")
		elif not self.references:
			status = _("Press BLUE to select services.")
		elif not self["list"].all_events:
			status = _("No EPG available for the selected services.")
		elif not self["list"].list:
			status = _("No events match the time filter.")
		else:
			status = _("Services: %d | Events: %d") % (len(self.references), len(self["list"].list))
		self["status"].setText(status)

	def setSortDescription(self):
		EPGSelection.setSortDescription(self)

	def yellowButtonPressed(self):
		self.sort_type = (self.sort_type + 1) % (3 if config.epg.ratingsort.value else 2)
		self["list"].reload(self.references, self.sort_type, self.filtering)
		self.setSortDescription()
		self.updateTitle()

	def fillFilteredSingleEPG(self, timespan):
		# Used by the inherited STOP, 1/4, 3/6 and filter-default actions.
		selected = event_key(self["list"].l.getCurrentSelection())
		self["list"].applyView(self.sort_type, self.filtering, selected=selected)
		self.updateTitle()

	def setSingleEpgTitle(self):
		self.updateTitle()

	def furtherOptions(self):
		from Screens.ChoiceBox import ChoiceBox
		from Components.PluginComponent import plugins
		from Plugins.Plugin import PluginDescriptor
		menu = []
		event = self["list"].getCurrent()[0]
		if event:
			for plugin in plugins.getPlugins(where=PluginDescriptor.WHERE_EVENTINFO):
				if 'selectedevent' in plugin.fnc.__code__.co_varnames:
					menu.append((plugin.name, lambda plugin=plugin: self.runPlugin(plugin)))
		menu.append((_("Timer Overview"), self.openTimerOverview))
		keys = (["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "red", "green", "yellow", "blue"] + ["dummy"] * len(menu))[:len(menu)]
		menu.append((_("Settings"), self.openSettings))
		keys.append("menu")
		def selected(choice):
			if choice:
				choice[1]()
		self.session.openWithCallback(selected, ChoiceBox, title=_("Select action"), list=menu, keys=keys)

	def openDurationFilter(self):
		from .settings import CustomEPGDurationSetup
		self.session.openWithCallback(self.durationFilterSelected,
			CustomEPGDurationSetup, self["list"].minimum_duration)

	def durationFilterSelected(self, minutes):
		if minutes is None:
			return
		self["list"].minimum_duration = minutes
		selected = event_key(self["list"].l.getCurrentSelection())
		self["list"].applyView(self.sort_type, self.filtering, selected=selected)
		self.updateTitle()

	def openSettings(self):
		from .settings import CustomEPGSetup
		self.session.openWithCallback(self.settingsSaved, CustomEPGSetup)

	def settingsSaved(self, saved=False):
		if saved:
			self["list"].minimum_duration = int(cfg.minimum_duration.value)
			self.reloadEPG()

	def blueButtonPressed(self):
		self.serviceEditorAlphabet = cfg.alphabetsort.value
		self.serviceEditorHideStarted = cfg.hide_started.value
		self.session.openWithCallback(self.servicesEdited, CustomEPGServiceEditor)

	def servicesEdited(self, saved=False):
		if saved:
			self.reloadEPG()
		elif (getattr(self, "serviceEditorAlphabet", cfg.alphabetsort.value) != cfg.alphabetsort.value
				or getattr(self, "serviceEditorHideStarted", cfg.hide_started.value) != cfg.hide_started.value):
			self.settingsSaved(True)

	def zapTo(self):
		cur = self["list"].getCurrent()
		if cur and cur[1]:
			self.session.nav.playService(cur[1].ref)
			self.close(True)

	def prevService(self):
		# PREV / NEXT in OpenPLi's EPGSelectActions.
		if self["list"].instance is not None and self["list"].list:
			self["list"].instance.moveSelectionTo(0)

	def nextService(self):
		if self["list"].instance is not None and self["list"].list:
			self["list"].instance.moveSelectionTo(len(self["list"].list) - 1)

	def nextBouquet(self):
		self["list"].instance.moveSelection(self["list"].instance.pageDown)

	def prevBouquet(self):
		self["list"].instance.moveSelection(self["list"].instance.pageUp)

	def refreshTimerIcons(self):
		# Rebuild cached rows after returning from timer dialogs/overview.
		self["list"].l.invalidate()

	def onSelectionChanged(self):
		EPGSelection.onSelectionChanged(self)
		self.refreshTimerIcons()
		cur = self["list"].getCurrent()
		self["Service"].newService(cur[1].ref if cur and cur[1] else None)
		self["key_red"].setText(_("Zap") if cur and cur[1] else "")
