from os.path import exists
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import SCOPE_CONFIG, resolveFilename

from . import _
from .configuration import cfg


def main(session, **kwargs):
	from .ui import TimerPlannerSelection
	if exists(resolveFilename(SCOPE_CONFIG, "timerplanner.xml")):
		session.open(TimerPlannerSelection)
	else:
		from .services import TimerPlannerServiceEditor

		def servicesSaved(saved=False):
			if saved:
				session.open(TimerPlannerSelection)

		session.openWithCallback(servicesSaved, TimerPlannerServiceEditor)


def extensionsMain(session, **kwargs):
	# PluginDescriptor equality compares callbacks; keep this distinct from main
	# so removing the extensions entry cannot remove the plugin-menu entry.
	main(session, **kwargs)


def Plugins(**kwargs):
	name=_("TimerPlanner")
	descr=_("Timer planner for selected services")
	pluginList = [PluginDescriptor(name=name, description=descr, where=[PluginDescriptor.WHERE_PLUGINMENU], icon="timerplanner.png", fnc=main)]
	if cfg.extensionsmenu.value:
		pluginList.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=extensionsMain, needsRestart=False))
	if cfg.eventmenu.value:
		pluginList.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EVENTINFO, fnc=extensionsMain, needsRestart=False))
	if cfg.channelcontextmenu.value:
		pluginList.append(PluginDescriptor(name=name, where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU, fnc=extensionsMain, needsRestart=False))
	return pluginList
