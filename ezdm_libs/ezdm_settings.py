from frontend import JSON_Editor
from objects import EzdmObject
from util import save_json


class Settings(EzdmObject):
    def save():
        name = 'settings.json'
        dest = 'etc'
        return save_json(dest, name)


class SETTINGS(JSON_Editor):
    def __init__(self):
        self._name = 'settings'
        JSON_Editor.__init__(self)
        self._obj = Settings({})
        self._icons = None
