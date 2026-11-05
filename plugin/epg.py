from os.path import exists
from time import time

from Components.ActionMap import ActionMap
from Components.EpgList import EPGList, EPG_TYPE_SINGLE, Rect
from Components.Sources.StaticText import StaticText
from Components.config import config
from Screens.EpgSelection import EPGSelection
from Screens.MessageBox import MessageBox
from Tools.Directories import SCOPE_CONFIG, resolveFilename
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, eLabel, eSize

from . import _
from .epgdata import collect_events, event_key, selection_index, sort_events
from .services import CustomEPGServiceEditor, service_name
from .storage import load_legacy_services, load_services


class CustomEPGList(EPGList):
	"""SingleEPG rows with an additional service column and a shared event list."""
	def __init__(self, selChangedCB, timer):
		EPGList.__init__(self, type=EPG_TYPE_SINGLE, selChangedCB=selChangedCB, timer=timer)
		self.list = []
		self.all_events = []
		self.service_names = {}

	def applySkin(self, desktop, parent):
		result = EPGList.applySkin(self, desktop, parent)
		self.l.setFont(2, gFont(self.eventTimeFont.family, self.eventTimeFont.pointSize + 4))
		return result

	def recalcEntrySize(self):
		EPGList.recalcEntrySize(self)
		if self.sorting == 2:
			r = self.rating_rect
			self.rating_rect = Rect(r.x + 10, r.y, r.w - 10, r.h)
		# Preserve SingleEPG's weekday/date columns, fonts and row height.
		# Split only its event area, after any rating column has been reserved.
		event = self.descr_rect
		# SingleEPG reserves 60 pixels only in rating mode. Reserve the same
		# space in every mode so the service and event columns never jump.
#		if self.sorting != 2:
#			event = Rect(event.x, event.y, max(0, event.w - 60), event.h)
		font = gFont(self.eventTimeFont.family, self.eventTimeFont.pointSize + 4)
		# Match the date column to the actual enlarged text, instead of leaving
		# SingleEPG's unused right-aligned space between time and event.
		date_width = max(eLabel.calculateTextSize(font, "%s%s.%s%s, %s%s:%s%s" % ((digit,) * 8), eSize(2000, event.h), True).width() for digit in "0123456789")
		gap = max(4, self.datetime_rect.x - self.weekday_rect.x - self.weekday_rect.w)
		self.datetime_rect.w = date_width
		event_start = self.datetime_rect.x + date_width + gap
#		service_width = event.w // 4
		service_width = event.w // 4 + (6 if self.sorting != 2 else 0)
		self.descr_rect = Rect(event_start, event.y, max(0, event.x + event.w - service_width - self.colGap - event_start), event.h)
		self.service_rect = Rect(event.x + event.w - service_width, event.y, service_width, event.h)

	def buildSingleEntry(self, service, eventId, beginTime, duration, title):
		row = EPGList.buildSingleEntry(self, service, eventId, beginTime, duration, title)
		# SingleEPG offsets the event text after timer icons but keeps its full
		# width. Clip it to our narrower event column so it cannot cover the
		# service or rating columns.
		for index, entry in enumerate(row[1:], 1):
			if entry[0] == eListboxPythonMultiContent.TYPE_TEXT:
				entry = list(entry)
				# Keep secondary columns small; enlarge only the event title.
				entry[5] = 2 if index in (1, 2) else 1
				if index == 2:  # Date/time, immediately after the weekday.
					entry[6] = RT_HALIGN_LEFT | RT_VALIGN_CENTER
				if entry[-1] == title and self.descr_rect.x <= entry[1] < self.service_rect.x:
					entry[5] = 2
					entry[3] = max(0, self.descr_rect.x + self.sidesMargin + self.descr_rect.w - entry[1])
				row[index] = tuple(entry)
		r = self.service_rect
		row.append((eListboxPythonMultiContent.TYPE_TEXT,
			r.x + self.sidesMargin, r.y, r.w, r.h, 1,
			RT_HALIGN_LEFT | RT_VALIGN_CENTER,
			self.service_names.get(service, "<N/A>")))
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
		self.list = sort_events(rows, sorting, self.getEventRating)
		self.l.setList(self.list)
		self.recalcEntrySize()
		if self.instance is not None and self.list:
			self.instance.moveSelectionTo(selection_index(self.list, selected, now))
		self.selectionChanged()

	def sortSingleEPG(self, sorting):
		# OpenPLi's moveToEventId alone cannot identify a row across multiple services.
		selected = event_key(self.l.getCurrentSelection())
		self.sorting = sorting
		self.list = sort_events(self.list, sorting, self.getEventRating)
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
		self.skinName = ["CustomEPGSelection", "EPGSelection"]
		self["status"] = StaticText()
		self["list"] = CustomEPGList(self.onSelectionChanged, session.nav.RecordTimer)
		self["key_blue"].setText(_("Services"))
		self["key_red"].setText(_("Refresh"))
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
		title = "CustomEPG - " + (_("Time"), "A-Z", _("Rating"))[self.sort_type]
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
		self["list"].sortSingleEPG(self.sort_type)
		self.setSortDescription()
		self.updateTitle()

	def fillFilteredSingleEPG(self, timespan):
		# Used by the inherited STOP, 1/4, 3/6 and filter-default actions.
		selected = event_key(self["list"].l.getCurrentSelection())
		self["list"].applyView(self.sort_type, self.filtering, selected=selected)
		self.updateTitle()

	def setSingleEpgTitle(self):
		self.updateTitle()

	def blueButtonPressed(self):
		self.session.openWithCallback(self.servicesEdited, CustomEPGServiceEditor)

	def servicesEdited(self, saved=False):
		if saved:
			self.reloadEPG()

	def zapTo(self):
		# Red refreshes the shared list; no service is tuned just to read its EPG.
		self.reloadEPG()

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
		self["key_red"].setText(_("Refresh"))
