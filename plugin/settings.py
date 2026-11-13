from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.config import  ConfigSelection, configfile
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox

from . import _
from .configuration import cfg, duration_choices
from .ui import VERSION

class TimerPlannerSetup(Screen, ConfigListScreen, HelpableScreen):
	skin = """<screen name="TimerPlannerSetup" position="center,center" size="600,300" title="TimerPlanner - Settings">
		<widget source="key_red" render="Label" position="10,10" size="280,32" font="Regular;20" backgroundColor="#9f1313" halign="center" valign="center" />
		<widget source="key_green" render="Label" position="310,10" size="280,32" font="Regular;20" backgroundColor="#176517" halign="center" valign="center" />
		<widget name="config" position="10,55" size="580,110" scrollbarMode="showOnDemand" />
		<widget name="description" position="10,180" size="580,110" font="Regular;19" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = ["TimerPlannerSetup", "Setup"]
		self["description"] = Label()
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText("")
		self.setTitle(_("TimerPlanner v%s - Settings") % VERSION)
		self.entries = self.createSetup()
		ConfigListScreen.__init__(self, self.entries, session=session, on_change=self.configChanged, fullUI=True)
		self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		menu = []
		menu.append((_("Hide events"), cfg.hide_started, _("Hide finished events, or both finished and ongoing events.")))
		if cfg.hide_started.value != "true":
			menu.append((4 * " " + _("Cursor on current service"), cfg.currentservice, _("Set cursor to the currently playing event when opening TimerPlanner.")))
		menu.append((_("Hide events shorter than"), cfg.minimum_duration, _("Default setting for the minimum duration of displayed events.")))
		menu.append((_("Hide events longer than"), cfg.maximum_duration, _("Default setting for the maximum duration of displayed events.")))
		menu.append((_("Alphabetical sorting"), cfg.alphabetsort, _("Applies to 'A-Z' only. 'Standard' disables character conversion.")))
		menu.append((_("Always show rating"), cfg.showrating, _("Show rating column regardless of the selected sorting mode.")))
		menu.append((_("Show in extensions menu"), cfg.extensionsmenu, _("Show plugin 'TimerPlanner' in the extension menu.")))
		menu.append((_("Show in event menu"), cfg.eventmenu, _("Show plugin 'TimerPlanner' in the event menu.")))
		menu.append((_("Show in channels selection menu"), cfg.channelcontextmenu, _("Show plugin 'TimerPlanner' in the channel selection context menu.")))
		return menu

	def selectionChanged(self):
		current = self["config"].getCurrent()
		self["description"].setText(current[2] if current and len(current) > 2 else "")

	def configChanged(self):
		if self["config"].getCurrent()[1] == cfg.hide_started:
			self.entries = self.createSetup()
			self["config"].setList(self.entries)

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
		if cfg.hide_started.value == "true":
			cfg.currentservice.save()
		configfile.save()
		self.refreshPlugins()
		self.close(True)

	def keyCancel(self):
		if self["config"].isChanged() or cfg.currentservice.isChanged():
			self.session.openWithCallback(self.cancelConfirmed, MessageBox,
				_("Close without saving changes?"), MessageBox.TYPE_YESNO, default=False)
		else:
			self.close(False)

	def cancelConfirmed(self, answer):
		if answer:
			for entry in self.entries:
				entry[1].cancel()
			cfg.currentservice.cancel()
			self.close(False)

	def refreshPlugins(self):
		from Components.PluginComponent import plugins
		from Tools.Directories import SCOPE_PLUGINS, resolveFilename
		plugins.clearPluginList()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))


class TimerPlannerDurationSetup(TimerPlannerSetup):

	def __init__(self, session, minimum, maximum):
		TimerPlannerSetup.__init__(self, session)
		self.setTitle(_("Event duration - temporary setting"))
		self.duration = ConfigSelection(default=str(minimum), choices=duration_choices)
		self.maximum = ConfigSelection(default=str(maximum), choices=duration_choices)
		self.entries = [
			(_("Hide events shorter than"), self.duration, _("Temporary setting. Applies only until TimerPlanner is closed.")),
			(_("Hide events longer than"), self.maximum, _("Temporary setting. Applies only until TimerPlanner is closed.")),
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