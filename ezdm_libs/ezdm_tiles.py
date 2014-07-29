from frontend import JSON_Editor
from game_map import Tile


class TILES(JSON_Editor):
    def __init__(self):
        self._name = 'tile'
        JSON_Editor.__init__(self)
        self._icons = 'backgrounds'
        self._obj = Tile({})
