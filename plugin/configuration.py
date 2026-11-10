from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo

from . import _


config.plugins.customepg = ConfigSubsection()
config.plugins.customepg.hide_started = ConfigSelection(default="true", choices=[
	("false", _("No")),
	("ended", _("Finished")),
	("true", _("Finished and ongoing")),
])
duration_choices = [("0", _("No limit"))] + [(str(minutes), _("%d min") % minutes) for minutes in range(10, 241, 5)]
config.plugins.customepg.minimum_duration = ConfigSelection(default="0", choices=duration_choices)
config.plugins.customepg.maximum_duration = ConfigSelection(default="0", choices=duration_choices)
config.plugins.customepg.alphabetsort = ConfigSelection(default="standard", choices=[
	("standard", _("Standard")),
	("czsk", _("CS/SK")),
	("latin2", _("Latin2")),
	("latin2-ch", _("Latin2 with 'Ch'")),
])
config.plugins.customepg.showrating = ConfigYesNo(default=False)
config.plugins.customepg.extensionsmenu = ConfigYesNo(default=False)
config.plugins.customepg.eventmenu = ConfigYesNo(default=False)
config.plugins.customepg.channelcontextmenu = ConfigYesNo(default=False)
cfg = config.plugins.customepg
