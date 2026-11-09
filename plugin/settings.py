from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.config import  ConfigSelection, configfile, getConfigListEntry
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox

from . import _
from .configuration import cfg, duration_choices
from .ui import VERSION

class CustomEPGSetup(Screen, ConfigListScreen, HelpableScreen):
	skin = """<screen name="CustomEPGSetup" position="center,center" size="600,300" title="CustomEPG - Settings">
		<widget source="key_red" render="Label" position="10,10" size="280,32" font="Regular;20" backgroundColor="#9f1313" halign="center" valign="center" />
		<widget source="key_green" render="Label" position="310,10" size="280,32" font="Regular;20" backgroundColor="#176517" halign="center" valign="center" />
		<widget name="config" position="10,55" size="580,110" scrollbarMode="showOnDemand" />
		<widget name="description" position="10,180" size="580,110" font="Regular;19" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = ["CustomEPGSetup", "Setup"]
		self["description"] = Label()
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText("")
		self.setTitle(_("CustomEPG v%s - Settings") % VERSION)
		self.entries = [
			getConfigListEntry(_("Hide events"), cfg.hide_started, _("Hide finished events, or both finished and ongoing events.")),
			getConfigListEntry(_("Hide events shorter than"), cfg.minimum_duration, _("Default setting for the minimum duration of displayed events.")),
			getConfigListEntry(_("Hide events longer than"), cfg.maximum_duration, _("Default setting for the maximum duration of displayed events.")),
			getConfigListEntry(_("Alphabetical sorting"), cfg.alphabetsort, _("Applies to 'A-Z' only. 'Standard' disables character conversion.")),
			getConfigListEntry(_("Show in extensions menu"), cfg.extensionsmenu, _("Show plugin 'CustomEPG' in the extension menu.")),
			getConfigListEntry(_("Show in event menu"), cfg.eventmenu, _("Show plugin 'CustomEPG' in the event menu.")),
			getConfigListEntry(_("Show in channels selection menu"), cfg.channelcontextmenu, _("Show plugin 'CustomEPG' in the channel selection context menu.")),
		]
		ConfigListScreen.__init__(self, self.entries, session=session, fullUI=True)
		self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def selectionChanged(self):
		current = self["config"].getCurrent()
		self["description"].setText(current[2] if current and len(current) > 2 else "")

	def validDurationRange(self, minimum, maximum):
		if maximum and minimum > maximum:
			self.session.open(MessageBox,
				_("Maximum event duration must not be shorter than minimum event duration."),
				MessageBox.TYPE_ERROR)
			return False
		return True

	def keySave(self):
		if not self.validDurationRange(int(cfg.minimum_duration.value), int(cfg.maximum_duration.value)):
			return
		for entry in self.entries:
			entry[1].save()
		configfile.save()
		self.refreshPlugins()
		self.close(True)

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirmed, MessageBox,
				_("Close without saving changes?"), MessageBox.TYPE_YESNO, default=False)
		else:
			self.close(False)

	def cancelConfirmed(self, answer):
		if answer:
			for entry in self.entries:
				entry[1].cancel()
			self.close(False)

	def refreshPlugins(self):
		from Components.PluginComponent import plugins
		from Tools.Directories import SCOPE_PLUGINS, resolveFilename
		plugins.clearPluginList()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))


class CustomEPGDurationSetup(CustomEPGSetup):

	def __init__(self, session, minimum, maximum):
		CustomEPGSetup.__init__(self, session)
		self.setTitle(_("Event duration - temporary setting"))
		self.duration = ConfigSelection(default=str(minimum), choices=duration_choices)
		self.maximum = ConfigSelection(default=str(maximum), choices=duration_choices)
		self.entries = [
			getConfigListEntry(_("Hide events shorter than"), self.duration,
				_("Temporary setting. Applies only until CustomEPG is closed.")),
			getConfigListEntry(_("Hide events longer than"), self.maximum,
				_("Temporary setting. Applies only until CustomEPG is closed.")),
		]
		self["config"].setList(self.entries)
		self["key_green"].setText(_("Apply"))
		self["durationActions"] = ActionMap(["OkCancelActions"], {
			"cancel": self.keyCancel,
		}, -2)
		self.selectionChanged()

	def keySave(self):
		minimum = int(self.duration.value)
		maximum = int(self.maximum.value)
		if self.validDurationRange(minimum, maximum):
			self.close((minimum, maximum))

	def keyCancel(self):
		self.close(None)