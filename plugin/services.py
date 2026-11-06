from os.path import exists

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.Sources.StaticText import StaticText
from Screens.ChannelSelection import SimpleChannelSelection
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from ServiceReference import ServiceReference
from Tools.Directories import SCOPE_CONFIG, resolveFilename
from enigma import eServiceReference

from . import _
from .storage import load_legacy_services, load_services, save_services


def selectable(ref):
	return ref is not None and ref.valid() and not (
		ref.flags & (eServiceReference.isMarker | eServiceReference.isDirectory | eServiceReference.isGroup)
	)


def service_name(ref):
	name = ServiceReference(ref).getServiceName() or ""
	return name.replace("\xc2\x86", "").replace("\xc2\x87", "").replace("\x86", "").replace("\x87", "")


class CustomEPGChannelSelection(SimpleChannelSelection):
	"""OpenPLi's bouquet/service browser; return only an individual service."""
	def __init__(self, session):
		SimpleChannelSelection.__init__(self, session, _("Select service for CustomEPG"))
		self.skinName = "SimpleChannelSelection"

	def channelSelected(self):
		ref = self.getCurrentSelection()
		if ref is None or not ref.valid():
			return
		if ref.flags & eServiceReference.isDirectory:
			self.enterPath(ref)
			self.gotoCurrentServiceOrProvider(ref)
		elif selectable(ref):
			self.close(ref)


class CustomEPGServiceEditor(Screen):
	skin = """<screen name="CustomEPGServiceEditor" position="center,center" size="600,440" title="CustomEPG">
		<widget source="key_red" render="Label" position="10,10" size="140,32" font="Regular;20" backgroundColor="#9f1313" halign="center" valign="center" />
		<widget source="key_green" render="Label" position="155,10" size="140,32" font="Regular;20" backgroundColor="#176517" halign="center" valign="center" />
		<widget source="key_yellow" render="Label" position="300,10" size="140,32" font="Regular;20" backgroundColor="#8f7700" halign="center" valign="center" />
		<widget source="key_blue" render="Label" position="445,10" size="145,32" font="Regular;20" backgroundColor="#153b8f" halign="center" valign="center" />
		<widget name="config" position="10,55" size="580,325" font="Regular;22" itemHeight="25" scrollbarMode="showOnDemand" />
		<widget source="status" render="Label" position="10,390" size="580,40" font="Regular;18" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["CustomEPGServiceEditor", "Setup"]
		self.setTitle(_("CustomEPG - Services"))
		self["description"] = Label()
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)
		self.path = resolveFilename(SCOPE_CONFIG, "customepg.xml")
		self.load_error = None
		try:
			if exists(self.path):
				self.services = load_services(self.path)
			else:
				self.services = [(ref, service_name(ref)) for ref, name in
					load_legacy_services(resolveFilename(SCOPE_CONFIG, "customepg.json"))]
		except (OSError, ValueError) as error:
			self.services = []
			self.load_error = str(error)
		self.original = self.services[:]
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Remove"))
		self["key_blue"] = StaticText(_("Add"))
		self["config"] = MenuList([])
		self["status"] = StaticText()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions"], {
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.save,
			"yellow": self.remove,
			"blue": self.add,
			"menu": self.openSettings,
			"up": self["config"].up,
			"down": self["config"].down,
			"left": self["config"].pageUp,
			"right": self["config"].pageDown,
		}, -2)
		self.refresh()
		self.onLayoutFinish.append(self.reportLoadError)

	def setStatus(self, text):
		self["status"].setText(text)
		self["description"].setText(text)

	def reportLoadError(self):
		if self.load_error:
			self.session.open(MessageBox, _("Cannot load CustomEPG settings:\n%s") % self.load_error, MessageBox.TYPE_ERROR)

	def refresh(self, index=0):
		rows = []
		for ref, saved_name in self.services:
			# Let Enigma resolve the service, including its native <N/A> result.
			# The saved name is metadata, never a fallback hiding a missing service.
			rows.append((service_name(ref) or "<N/A>", ref))
		self["config"].setList(rows)
		if rows:
			self["config"].moveToIndex(min(index, len(rows) - 1))
		self.setStatus(_("Services: %d") % len(rows) if rows else _("Press BLUE to add a service from a bouquet."))

	def openSettings(self):
		from .settings import CustomEPGSetup
		self.session.open(CustomEPGSetup)

	def add(self):
		self.session.openWithCallback(self.serviceSelected, CustomEPGChannelSelection)

	def serviceSelected(self, ref=None):
		if not selectable(ref):
			return
		# compare strings ignore display names; retain the full reference (including IPTV URL).
		key = ref.toCompareString()
		for index, (existing, name) in enumerate(self.services):
			if eServiceReference(existing).toCompareString() == key:
				self["config"].moveToIndex(index)
				self.setStatus(_("This service is already selected."))
				return
		self.services.append((ref.toString(), service_name(ref)))
		self.refresh(len(self.services) - 1)

	def remove(self):
		current = self["config"].getCurrent()
		if current is not None:
			index = self["config"].getSelectedIndex()
			del self.services[index]
			self.refresh(index)

	def save(self):
		# A broken/unreadable file must not silently become an empty selection.
		if self.load_error:
			self.session.open(MessageBox, _("Settings could not be loaded. Fix the settings file before saving."), MessageBox.TYPE_ERROR)
			return
		try:
			save_services(self.path, self.services)
		except OSError as error:
			self.session.open(MessageBox, _("Cannot save CustomEPG settings:\n%s") % error, MessageBox.TYPE_ERROR)
			return
		self.close(True)

	def cancel(self):
		if self.services != self.original:
			self.session.openWithCallback(self.cancelConfirmed, MessageBox, _("Close without saving changes?"), MessageBox.TYPE_YESNO, default=False)
		else:
			self.close(False)

	def cancelConfirmed(self, answer):
		if answer:
			self.close(False)
