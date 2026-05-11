# i18n system for translations
# public api: register_language, _

class I18n:
    def __init__(self):
        self._trans = {}
        self._info = {}
        self._current = "en"
        self._callbacks = []

    def register_language(self, code, name, translations):
        self._info[code] = name
        self._trans[code] = translations

    def on_change(self, callback):
        self._callbacks.append(callback)

    def set_language(self, code):
        if code in self._info:
            self._current = code
            for cb in self._callbacks:
                cb()

    def _(self, key, **kwargs):
        text = self._trans.get(self._current, {}).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def get_languages(self):
        return [(k, v) for k, v in self._info.items()]

    def current(self):
        return self._current


_i18n = I18n()


def _(key, **kwargs):
    return _i18n._(key, **kwargs)


def register_language(code, name, translations):
    _i18n.register_language(code, name, translations)


def set_language(code):
    _i18n.set_language(code)


def on_change(callback):
    _i18n.on_change(callback)


def get_languages():
    return _i18n.get_languages()
