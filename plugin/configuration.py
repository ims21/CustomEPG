from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo

from . import _


config.plugins.timerplanner = ConfigSubsection()
config.plugins.timerplanner.hide_started = ConfigSelection(default="true", choices=[
	("false", _("No")),
	("ended", _("Finished")),
	("true", _("Finished and ongoing")),
])
config.plugins.timerplanner.currentservice = ConfigYesNo(default=False)
duration_choices = [("0", _("No limit"))] + [(str(minutes), _("%d min") % minutes) for minutes in range(10, 241, 5)]
config.plugins.timerplanner.minimum_duration = ConfigSelection(default="0", choices=duration_choices)
config.plugins.timerplanner.maximum_duration = ConfigSelection(default="0", choices=duration_choices)
config.plugins.timerplanner.alphabetsort = ConfigSelection(default="standard", choices=[
	("standard", _("Standard")),
	("czsk", _("CS/SK")),
	("latin2", _("Latin2")),
	("latin2-ch", _("Latin2 with 'Ch'")),
])
config.plugins.timerplanner.showrating = ConfigYesNo(default=False)
config.plugins.timerplanner.extensionsmenu = ConfigYesNo(default=False)
config.plugins.timerplanner.eventmenu = ConfigYesNo(default=False)
config.plugins.timerplanner.channelcontextmenu = ConfigYesNo(default=False)
cfg = config.plugins.timerplanner
