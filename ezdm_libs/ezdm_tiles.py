from frontend import JSON_Editor
from gamemap import Tile


class TILES(JSON_Editor):
    def __init__(self):
        self._name = 'tile'
        JSON_Editor.__init__(self)
        self._icons = 'backgrounds'
        self._obj = Tile({})
