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
        print "Trying to remove %s from %s objtype %s" % (name, current, objtype)
        if name in current:
            del(current[current.index(name)])
        self.put('/conditional/%s' % objtype, current)

    def list(self, objtype):
        return self.get('/conditional/%s' % objtype, [])

    def onenter(self, player, page):
        event(self, "/conditional/events/onenter", {'tile': self, 'page': page, 'player': player})


class GameMap(EzdmObject):

    def __init__(self, json={}, name='', max_x=25, max_y=15, lightradius=1):
        if not json:
            self.new(name=name, max_x=max_x, max_y=max_y, lightradius=lightradius)
        else:
            self.json = json

        if not 'lightradius' in self.json:
            self.json['lightradius'] = lightradius
        for y in range(0, self.json['max_y']):
            for x in range(0, self.json['max_x']):
                tile = self.tile(x, y)
                players = tile.get('/conditional/players', [])
                if players:
                    for player in players:
                        j = EzdmObject(load_json('characters', player))
                        loc = j.get('/core/location', {})
                        if not '.json' in loc['map']:
                            loc['map'] = '%s.json' % loc['map']
                        if not loc['map'] == self.name() or not int(loc['x']) == x or not int(loc['y']) == y:
                            self.removefromtile(x, y, player, 'players')

    def new(self, name='', max_x=25, max_y=15, lightradius=1):
        self.json = {'name': name}
        self.json['max_x'] = max_x
        self.json['max_y'] = max_y
        self.json['tiles'] = [[{}] * max_x for _ in range(max_y)]

    def load_tile(self, x, y, tile):
        tjson = load_json('tiles', tile)
        self.load_tile_from_json(x, y, tjson)

    def load_tile_from_json(self, x, y, json):
        self()['tiles'][y][x] = json

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
        print tile
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
                out.append((thingy.replace('.json', ''), readkey('/core/icon', json, ''), section))
        money = self.getmoney(x, y)
        if money[0] or money[1] or money[2]:
            out.append(('money', 'icons/money.png', 'money'))
        if not unique:
            return out
        else:
            return list(set(out))

    def name(self):
        name = '%s.json' % self.get('name', '').lower().replace(' ', '_')
        return name

    def save(self):
        return save_json('maps', self.name(), self())

    def reveal(self, x, y, xtraradius=0):
        radius = int(self.get('lightradius', 1)) + xtraradius
        #TODO prevent looking through walls
        max_x = int(self.get('max_x', 1))
        max_y = int(self.get('max_y', 1))
        print "x", x, "max_x", max_x, "y", y, "max_y", max_y
        print max_x
        left = x - radius
        if left < 0:
            left = 0
        right = x + radius + 1
        if right > max_x:
            right = max_x
        top = y - radius
        if top < 0:
            top = 0
        bottom = y + radius + 1
        if bottom > max_y:
            bottom = max_y
        print "left", left, "top", top, "right", right, "bottom", bottom
        for pt_y in range(top, bottom):
            for pt_x in range(left, right):
                tile = self.tile(pt_x, pt_y)
                tile.put('/core/revealed', True)
                self.load_tile_from_json(pt_x, pt_y, tile())
        self.save()
