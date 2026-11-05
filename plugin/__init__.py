import gettext
from os.path import dirname, join


def _(text):
	translated = gettext.dgettext("CustomEPG", text)
	return translated if translated != text else gettext.gettext(text)


gettext.bindtextdomain("CustomEPG", join(dirname(__file__), "locale"))
