from frontend import JSON_Editor
from character import Character

class CHARACTERS(JSON_Editor):
    def __init__(self):
        self._name = 'character'
        JSON_Editor.__init__(self)
        self._obj = Character({})