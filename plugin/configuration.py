from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo

from . import _


config.plugins.customepg = ConfigSubsection()
config.plugins.customepg.alphabetsort = ConfigSelection(default="standard", choices=[
	("standard", _("Standard")),
	("czsk", _("CS/SK")),
	("latin2", _("Latin2")),
	("latin2-ch", _("Latin2 with 'Ch'")),
])
config.plugins.customepg.extensionsmenu = ConfigYesNo(default=False)
config.plugins.customepg.eventmenu = ConfigYesNo(default=False)
config.plugins.customepg.channelcontextmenu = ConfigYesNo(default=False)
config.plugins.customepg.hide_started = ConfigYesNo(default=True)
cfg = config.plugins.customepg
