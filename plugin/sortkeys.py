"""Alphabetic keys, independent of Enigma2 configuration and GUI.

Character mappings and Ch ordering adapted from ims21/MovieManager,
plugin/dictsort.py. Keys are converted once and cached with a bounded LRU.
"""
from functools import lru_cache


dictSortCZSK = {
	u'\xc1': 'A{',		# A acute
	u'\xc4': 'A|',		# A diaeresis (umlaut)
	u'\u010c': 'C{',	# C caron
	u'\u010e': 'D{',	# D caron
	u'\xc9': 'E{',		# E acute
	u'\u011a': 'E|',	# E caron
	u'\xcb': 'E}',		# E diaeresis (umlaut)
	u'\xcd': 'I{',		# I acute
#	u'\xcf': 'I|',		# I diaeresis (umlaut)
	u'\u0139': 'L{',	# L acute
	u'\u013d': 'L|',	# L caron
#	u'\u0141': 'L}',	# L with stroke
	u'\u0147': 'N{',	# N caron
	u'\xd3': 'O{',		# O acute
	u'\xd4': 'O|',		# O circumflex (vokan)
	u'\xd6': 'O}',		# O diaeresis (umlaut)
#	u'\u0154': 'R{',	# R acute
	u'\u0158': 'R|',	# R caron
	u'\u0160': 'S{',	# S caron
	u'\u0164': 'T{',	# T caron
	u'\xda': 'U{',		# U acute
	u'\u016e': 'U|',	# U ring
	u'\xdc': 'U}',		# U diaeresis (umlaut)
	u'\xdd': 'Y{',		# Y acute
	u'\u0178': 'Y|',	# Y diaeresis (umlaut)
	u'\u017d': 'Z{',	# Z caron
	u'\xe1': 'a{',		# a acute
	u'\xe4': 'a|',		# a diaeresis (umlaut)
	u'\u010d': 'c{',	# c caron
	u'\u010f': 'd{',	# d caron
	u'\xe9': 'e{',		# e acute
	u'\u011b': 'e|',	# e caron
	u'\xeb': 'e}',		# e diaeresis (umlaut)
	u'\xed': 'i{',		# i caron
#	u'\xef': 'i|',		# i diaeresis (umlaut)
	u'\u013a': 'l{',	# l acute
	u'\u013e': 'l|',	# l caron
#	u'\u0142': 'l}',	# l with stroke
	u'\u0148': 'n{',	# n caron
	u'\xf3': 'o{',		# o acute
	u'\xf4': 'o|',		# o circumflex (vokan)
	u'\xf6': 'o}',		# o diaeresis (umlaut)
#	u'\u0155': 'r{',	# r acute
	u'\u0159': 'r|',	# r caron
	u'\u0161': 's{',	# s caron
	u'\u0165': 't{',	# t caron
	u'\xfa': 'u{',		# u acute
	u'\u016f': 'u|',	# u ring
	u'\xfc': 'u}',		# u diaeresis (umlaut)
	u'\xfd': 'y{',		# y acute
	u'\xff': 'y|',		# y diaeresis (umlaut)
	u'\u017e': 'z{'		# z caron
}

dictSortLatin2 = {
	u'\xc1': 'A{',		# A acute
	u'\xc2': 'A|',		# A circumflex
	u'\u0102': 'A}',	# A breve
	u'\xc4': 'A~',		# A diaeresis (umlaut)
	u'\u0104': 'A~{',	# A ogonek
	u'\u0106': 'C{',	# C acute
	u'\xc7': 'C|',		# C cedilla
	u'\u010c': 'C}',	# C caron
	u'\u010e': 'D{',	# D caron
	u'\u0110': 'D|',	# D stroke
	u'\xc9': 'E{',		# E acute
	u'\u0118': 'E|',	# E ogonek
	u'\xcb': 'E}',		# E diaeresis (umlaut)
	u'\u011a': 'E~',	# E caron
	u'\xcd': 'I{',		# I acute
	u'\xce': 'I|',		# I circumflex
#	u'\xcf': 'I}',		# I diaeresis (umlaut)
	u'\u0139': 'L{',	# L acute
	u'\u013d': 'L|',	# L caron
	u'\u0141': 'L}',	# L with stroke
	u'\u0143': 'N{',	# N acute
	u'\u0147': 'N|',	# N caron
	u'\xd3': 'O{',		# O acute
	u'\xd4': 'O|',		# O circumflex (vokan)
	u'\u0150': 'O}',	# O double acute
	u'\xd6': 'O~',		# O diaeresis (umlaut)
	u'\u0154': 'R{',	# R acute
	u'\u0158': 'R|',	# R caron
	u'\u015A': 'S{',	# S acute
	u'\u0160': 'S|',	# S caron
	u'\u015E': 'S}',	# S cedilla
	u'\u0164': 'T{',	# T caron
	u'\u0162': 'T|',	# T cedilla
	u'\xda': 'U{',		# U acute
	u'\u016e': 'U|',	# U ring
	u'\xdc': 'U}',		# U diaeresis (umlaut)
	u'\u0170': 'U~',	# U double acute
	u'\xdd': 'Y{',		# Y acute
#	u'\u0178': 'Y|',	# Y diaeresis (umlaut)
	u'\u0179': 'Z{',	# Z acute
	u'\u017d': 'Z|',	# Z caron
	u'\u017b': 'Z}',	# Z dot above
	u'\xe1': 'a{',		# a acute
	u'\xe2': 'a|',		# a circumflex
	u'\u0103': 'a}',	# a breve
	u'\xe4': 'a~',		# a diaeresis (umlaut)
	u'\u0105': 'a~{',	# a ogonek
	u'\u0107': 'c{',	# c acute
	u'\xe7': 'c|',		# c cedilla
	u'\u010d': 'c}',	# c caron
	u'\u010f': 'd{',	# d caron
	u'\u0111': 'd|',	# d stroke
	u'\xe9': 'e{',		# e acute
	u'\u0119': 'e|',	# e ogonek
	u'\u011b': 'e}',	# e caron
	u'\xeb': 'e~',		# e diaeresis (umlaut)
	u'\xed': 'i{',		# i acute
	u'\xee': 'i|',		# i circumflex
#	u'\xef': 'i}',		# i diaeresis (umlaut)
	u'\u013a': 'l{',	# l acute
	u'\u013e': 'l|',	# l caron
	u'\u0142': 'l}',	# l with stroke
	u'\u0144': 'n{',	# n acute
	u'\u0148': 'n|',	# n caron
	u'\xf3': 'o{',		# o acute
	u'\xf4': 'o|',		# o circumflex (vokan)
	u'\u0151': 'o}',	# o double acute
	u'\xf6': 'o~',		# o diaeresis (umlaut)
	u'\u0155': 'r{',	# r acute
	u'\u0159': 'r|',	# r caron
	u'\u015b': 's{',	# s acute
	u'\u0161': 's|',	# s caron
	u'\u015f': 's}',	# s cedilla
	u'\u0165': 't{',	# t caron
	u'\u0163': 't|',	# t cedilla
	u'\xfa': 'u{',		# u acute
	u'\u016f': 'u|',	# u ring
	u'\xfc': 'u}',		# u diaeresis (umlaut)
	u'\u0171': 'u~',	# u double acute
	u'\xfd': 'y{',		# y acute
#	u'\xff': 'y|',		# y diaeresis (umlaut)
	u'\u017a': 'z{',	# z acute
	u'\u017e': 'z|',	# z caron
	u'\u017c': 'z}'		# z dot above

}


_TRANSLATIONS = {
	"czsk": str.maketrans(dictSortCZSK),
	"latin2": str.maketrans(dictSortLatin2),
	"latin2-ch": str.maketrans(dictSortLatin2),
}


@lru_cache(maxsize=8192)
def alphabetic_key(text, mode):
	mapping = _TRANSLATIONS.get(mode)
	if mapping is None:
		return text.lower()
	text = text.translate(mapping)
	if mode in ("czsk", "latin2-ch"):
		text = text.replace('ch', 'h}').replace('Ch', 'H|').replace('CH', 'H{').replace('cH', 'h~')
	return text.lower()
