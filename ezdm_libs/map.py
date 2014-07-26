from objects import EzdmObject
from util import save_json


class Tile(EzdmObject):
    json = {}

    def __init__(self, json):
        self.json = json

    def tiletype(self):
        return self.get('/core/type', 'floor')

    def background(self):
        return self.get('/core/background')

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('maps/tiles', name.lower().replace(' ', '_'), self.json)
