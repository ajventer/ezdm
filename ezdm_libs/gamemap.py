from objects import EzdmObject, event
from util import save_json, load_json, readkey


class Tile(EzdmObject):
    json = {}

    def tiletype(self):
        return self.get('/core/type', 'floor')

    def linktarget(self, target=None, x=0, y=0):
        if not target:
            return self.get('/conditional/newmap', {})
        else:
            self.put('/conditional/newmap', {'mapname': target, "x": x, "y": y})

    def background(self):
        return self.get('/core/background')

    def canenter(self, new=None):
        if new is None:
            return self.get('/conditional/canenter', False)
        self.put('/conditional/canenter', new)

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('tiles', name.lower().replace(' ', '_'), self.json)

    def add(self, name, objtype):
        if not name.endswith('.json'):
            name = '%s.json' % name
        current = self.get('/conditional/%s' % objtype, [])
        current.append(name)
        self.put('/conditional/%s' % objtype, current)

    def remove(self, name, objtype):
        if not name.endswith('.json'):
            name = '%s.json' % name
        current = self.get('/conditional/%s' % objtype, [])
        del(current[current.index(name)])
        self.put('/conditional/%s' % objtype, current)

    def list(self, objtype):
        return self.get('/conditional/%s' % objtype, [])

    def onenter(self, player, page):
        event(self, "/conditional/events/onenter", {'tile': self, 'page': page, 'player': player})


class GameMap(EzdmObject):

    def __init__(self, json={}, name='', max_x=25, max_y=15):
        if not json:
            self.new(name=name, max_x=max_x, max_y=max_y)
        else:
            self.json = json

    def new(self, name='', max_x=25, max_y=15):
        self.json = {'name': name}
        self.json['max_x'] = max_x
        self.json['max_y'] = max_y
        self.json['tiles'] = [[{}] * max_x for _ in range(max_y)]

    def load_tile(self, x, y, tile):
        tjson = load_json('tiles', tile)
        self()['tiles'][y][x] = tjson

    def tile(self, x, y):
        return Tile(self()['tiles'][y][x])

    def putmoney(self, x, y, gold, silver, copper):
        tile = self.tile(x, y)
        tile.put('/conditional/gold', gold)
        tile.put('/conditional/silver', silver)
        tile.put('/conditional/copper', copper)
        self()['tiles'][y][x] = tile()

    def getmoney(self, x, y):
        tile = self.tile(x, y)
        return (int(tile.get('/conditional/gold', 0)), int(tile.get('/conditional/silver', 0)), int(tile.get('/conditional/copper', 0)))

    def addtotile(self, x, y, name, objtype):
        tile = self.tile(x, y)
        tile.add(name, objtype)
        self()['tiles'][y][x] = tile()

    def removefromtile(self, x, y, name, objtype):
        tile = self.tile(x, y)
        tile.remove(name, objtype)
        self()['tiles'][y][x] = tile()

    def tile_icons(self, x, y, unique=False):
        tile = self.tile(x, y)
        if not tile():
            return {}
        out = []
        sources = {'items': 'items', 'npcs': 'characters', 'players': 'characters'}
        for section in ['items', 'npcs', 'players']:
            for thingy in tile.get('/conditional/%s' % section, []):
                json = load_json(sources[section], thingy)
                out.append((thingy.replace('.json', ''), readkey('/core/icon', json, '')))
        money = self.getmoney(x, y)
        if money[0] or money[1] or money[2]:
            out.append('money', 'icons/money.png')
        if not unique:
            return out
        else:
            return list(set(out))

    def name(self):
        name = '%s.json' % self.get('name', '').lower().replace(' ', '_')
        return name

    def save(self):
        return save_json('maps', self.name(), self())
