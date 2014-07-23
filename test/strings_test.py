from onionshare.strings import *

def test_load_strings_defaults_to_english():
    "load_strings() loads English by default"
    locale.getdefaultlocale = lambda: ('en_US', 'UTF-8')
    strings = Strings()
    assert strings.get('calculating_sha1') == "Calculating SHA1 checksum."

def test_load_strings_loads_other_languages():
    "load_strings() loads other languages in different locales"
    locale.getdefaultlocale = lambda: ('fr_FR', 'UTF-8')
    strings = Strings('fr')
    assert strings.get('calculating_sha1') == "Calculer un hachage SHA-1."

def test_load_strings_falls_back_to_english():
    "load_strings() uses English strings if a language is not found"
    locale.getdefaultlocale = lambda: ('pl_PL', 'UTF-8')
    pl_strings = Strings()
    en_strings = Strings('en')
    assert pl_strings.strings == en_strings.strings
