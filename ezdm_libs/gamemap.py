from objects import EzdmObject
from util import save_json, load_json


class Tile(EzdmObject):
    json = {}

    def tiletype(self):
        return self.get('/core/type', 'floor')

    def background(self):
        return self.get('/core/background')

    def canenter(self, new=None):
        if new is None:
            return self.get('/core/canenter', False)
        self.put('/core/canenter', new)

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('tiles', name.lower().replace(' ', '_'), self.json)


class GameMap(EzdmObject):

    def __init__(self, json={}, name=None):
        if not json:
            self.new(name)
        else:
            self.json = json

    def new(self, name=''):
        self.json = {'name': name}
        self.json['tiles'] = [[{}] * 20 for _ in range(20)]

    def load_tile(self, x, y, tile):
        tjson = load_json('tiles', tile)
        self()['tiles'][x][y] = tjson

    def tile(self, x, y):
        return Tile(self()['tiles'][x][y])
