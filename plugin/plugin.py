from Plugins.Plugin import PluginDescriptor

from . import _
from .configuration import cfg


def main(session, **kwargs):
	from .epg import CustomEPGSelection
	session.open(CustomEPGSelection)


def extensionsMain(session, **kwargs):
	# PluginDescriptor equality compares callbacks; keep this distinct from main
	# so removing the extensions entry cannot remove the plugin-menu entry.
	main(session, **kwargs)


def Plugins(**kwargs):
	name=_("CustomEPG")
	descr=_("EPG for selected services")
	pluginList = [PluginDescriptor(name=name, description=descr, where=[PluginDescriptor.WHERE_PLUGINMENU], icon="custepg.png", fnc=main)]
	if cfg.extensionsmenu.value:
		pluginList.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=extensionsMain, needsRestart=False))
	if cfg.eventmenu.value:
		pluginList.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EVENTINFO, fnc=extensionsMain, needsRestart=False))
	if cfg.channelcontextmenu.value:
		pluginList.append(PluginDescriptor(name=name, where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU, fnc=extensionsMain, needsRestart=False))
	return pluginList
