import inspect, json, locale, os

class Strings(object):

    def __init__(self, language='en'):
        self.strings = {}
        self.onionshare_dir = self._current_dir()
        self._load_strings(language)

    def get(self, string):
        return self.strings[string]

    def _load_strings_from(self, directory):
        return json.loads(open('{0}/strings.json'.format(directory)).read())

    def _load_translations(self):
        try:
            return self._load_strings_from(os.getcwd())
        except IOError:
            return self._load_strings_from(self.onionshare_dir)

    def _override_default_language(self, strings, translated, language):
        lc, enc = locale.getdefaultlocale()
        if lc:
            lang = lc[:2]
            if lang in translated:
                # if a string doesn't exist, fallback to English
                for key in translated[language]:
                    if key in translated[lang]:
                        strings[key] = translated[lang][key]
        return strings

    def _load_strings(self, language):
        translations = self._load_translations()
        strings = translations[language]
        self.strings = self._override_default_language(strings, translations, language)

    def _current_dir(self):
        return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
