from util import save_json, load_json
from character import Character
from gamemap import GameMap
from objects import EzdmObject


class Campaign(EzdmObject):

    def __init__(self, json):
        self.json = json
        self.put('/core/current_char', 0)
        self.chars_in_round()
        if self.characters:
            self.character = self.characters[0]
        self.messages = []

    def chars_in_round(self):
        chars = []
        maps_parsed = []
        players = self.get('/core/players', [])
        for player in sorted(players):
            if not player.endswith('.json'):
                player = '%s.json' % player
            p = Character(load_json('characters', player))
            if not p in chars:
                p.set_index(len(chars))
                print "player", player, p.index
                chars.append(p)
        for player in sorted(players):
            p = Character(load_json('characters', player))
            loc = p.get('/core/location/', '')
            mapname = loc['map']

            if not mapname in maps_parsed:
                maps_parsed.append(mapname)
            else:
                continue
            gamemap = GameMap(load_json('maps', mapname))
            for y in range(0, gamemap.get('/max_y', 1)):
                for x in range(0, gamemap.get('/max_x', 1)):
                    tile = gamemap.tile(x, y)
                    if tile.get('/core/revealed', False) is True:
                        npcs_here = tile.get('/conditional/npcs', [])
                        for npc in sorted(npcs_here):
                            n = Character(load_json('characters', npc))
                            if n.get('/conditional/orientation', 'friendly').strip() == 'aggressive':
                                n.put('/core/location', {"map": mapname, "x": x, "y": y})
                                n.set_index(len(chars))
                                print npc, n.index
                                chars.append(n)
        self.characters = list(set(chars))

    def current_char(self):
            return self.character

    def endround(self):
        next_char = int(self.get('/core/current_char', 0))
        next_char += 1
        if next_char >= len(self.characters):
            next_char = 0
        self.put('/core/current_char', next_char)
        self.character = self.characters[next_char]
        loc = self.character.get('/core/location', {})
        print loc
        if loc:
            self.character.moveto(mapname=loc['map'], x=loc['x'], y=loc['y'])

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('campaigns', name.lower().replace(' ', '_'), self.json)

    def message(self, s):
        self.messages.append((s, 'messages'))

    def warning(self, s):
        self.messages.append((s, 'warnings'))

    def error(self, s):
        self.messages.append((s, 'errors'))
