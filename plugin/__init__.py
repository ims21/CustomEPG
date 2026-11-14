import gettext
from os.path import dirname, join


def _(text):
	translated = gettext.dgettext("TimerPlanner", text)
	return translated if translated != text else gettext.gettext(text)


def ngettext(singular, plural, n):
	translated = gettext.dngettext("TimerPlanner", singular, plural, n)
	return translated if translated not in (singular, plural) else gettext.ngettext(singular, plural, n)


gettext.bindtextdomain("TimerPlanner", join(dirname(__file__), "locale"))
