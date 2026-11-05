from Plugins.Plugin import PluginDescriptor

from . import _


def main(session, **kwargs):
	from .epg import CustomEPGSelection
	session.open(CustomEPGSelection)


def Plugins(**kwargs):
	return [PluginDescriptor(
		name="CustomEPG",
		description=_("EPG for selected services"),
		where=[
			PluginDescriptor.WHERE_PLUGINMENU,
			PluginDescriptor.WHERE_EXTENSIONSMENU,
		],
		fnc=main,
	)]
