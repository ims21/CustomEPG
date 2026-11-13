import gettext
from os.path import dirname, join


def _(text):
	translated = gettext.dgettext("TimerPlanner", text)
	return translated if translated != text else gettext.gettext(text)


gettext.bindtextdomain("TimerPlanner", join(dirname(__file__), "locale"))
