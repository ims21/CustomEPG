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


def syncExtensionsMenu():
	from os.path import dirname
	from Components.PluginComponent import plugins
	entries = [p for p in plugins.getPlugins(PluginDescriptor.WHERE_EXTENSIONSMENU)
		if p.fnc is extensionsMain]
	if cfg.extensionsmenu.value:
		if not entries:
			entry = PluginDescriptor(name="CustomEPG", description=_("EPG for selected services"),
				where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon="custepg.png", fnc=extensionsMain, needsRestart=False)
			entry.updateIcon(dirname(__file__))
			plugins.addPlugin(entry)
	else:
		for entry in entries:
			plugins.removePlugin(entry)


def Plugins(**kwargs):
	name="CustomEPG"
	descr=_("EPG for selected services")
	pluginList = [PluginDescriptor(name=name, description=descr, where=[PluginDescriptor.WHERE_PLUGINMENU], icon="custepg.png", fnc=main)]
	if cfg.extensionsmenu.value:
		pluginList.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon="custepg.png", fnc=extensionsMain, needsRestart=False))
	return pluginList
