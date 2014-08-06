from util import save_json, load_json, rolldice
from character import Character
from gamemap import GameMap
from objects import EzdmObject


class Campaign(EzdmObject):

    def __init__(self, json):
        self.rounds = 0
        self.json = json
        self.charcounter = -1
        self.chars_in_round()
        self.messages = []

    def list_chars(self):
        for char in self.characters:
            print char.displayname()

    def addmap(self, mapname):
        maps = self.get('/core/maps', [])
        if not isinstance(maps, list):
            maps = []
        maps.append(mapname)
        self.json['core']['maps'] = list(set(maps))
        self.save()

    def players(self):
        return self.get('/core/players', [])

    def chars_in_round(self):
        self.icons = {}
        chars = []
        players = self.players()
        print players
        for player in sorted(players):
            if not player.endswith('.json'):
                player = '%s.json' % player
            p = Character(load_json('characters', player))
            if not p in chars and p.get('/core/combat/hitpoints', 0) > 0:
                p.set_index(len(chars))
                print "player", player, p.index
                chars.append(p)
                loc = p.get('/core/location', {})
                mapname = loc['map']
                if not mapname in self.icons:
                    self.icons[mapname] = {}
                if not (loc['x'], loc['y']) in self.icons[mapname]:
                    self.icons[mapname][(loc['x'], loc['y'])] = []
                self.icons[mapname][(loc['x'], loc['y'])].append(p)
        print self.get('/core/maps', [])
        for mapname in self.get('/core/maps', []):
            if not mapname in self.icons:
                    self.icons[mapname] = {}
            gamemap = GameMap(load_json('maps', mapname))
            for y in range(0, gamemap.get('/max_y', 1)):
                for x in range(0, gamemap.get('/max_x', 1)):
                    tile = gamemap.tile(x, y)
                    if tile.revealed():
                        npcs_here = tile.get('/conditional/npcs', [])
                        for npc in sorted(npcs_here):
                            n = Character(npc)
                            print "   Found %s" % n.displayname()
                            n.put('/core/location', {"map": mapname, "x": x, "y": y})
                            n.set_index(len(chars))
                            if not (x, y) in self.icons[mapname]:
                                self.icons[mapname][(x, y)] = []
                            self.icons[mapname][(x, y)].append(n)
                            chars.append(n)
        self.characters = chars

    def current_char(self):
            return self.character

    @property
    def character(self):
        return self.characters[self.charcounter]

    def roll_for_initiative(self):
        print "Before rolling initiative", self.characters
        initiative = []
        self.message('Rolling for initiative:')
        for char in self.characters:
            roll = rolldice(numdice=1, numsides=20, modifier=0)
            self.message('%s %s' % (char.displayname(), roll[1]))
            initiative.append((roll[0], char))
        self.characters = []
        print "Unsorted", initiative, "Sorted", sorted(initiative, reverse=True)
        for char in sorted(initiative, reverse=True):
            self.characters.append(char[1])
        print "After rolling initiave", self.characters
        self.message('%s rolled the highest and goes first' % self.characters[0].displayname())

    def endturn(self):
        self.error('End of turn. Starting new turn.')
        self.chars_in_round()
        #self.roll_for_initiative()

    def endround(self):
        print "Charcounter - start:", self.charcounter, "Characters", self.characters
        self.rounds += 1
        next_char = self.charcounter
        print "Next char:", next_char
        char_health = 0
        cycle = False
        while char_health == 0:
            next_char += 1
            print "Next char in loop", next_char
            if next_char >= len(self.characters):
                if not cycle:
                    cycle = True
                else:
                    self.error('All characters are dead !')
                    break
                next_char = 0
                print "Next char reset", next_char
                self.endturn()
            char_health = int(self.characters[next_char].get('/core/combat/hitpoints', 0))
        print "After loop nextchar", next_char, "charcounter", self.charcounter
        self.charcounter = next_char
        print "After loop nextchar", next_char, "charcounter", self.charcounter
        self.onround(self.character)
        loc = self.character.get('/core/location', {})
        print loc
        if loc:
            self.character.moveto(mapname=loc['map'], x=loc['x'], y=loc['y'])
        self.error('%s goes next' % self.character.displayname())
        print "Charcounter - end:", self.charcounter

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('campaigns', name.lower().replace(' ', '_'), self.json)

    def message(self, s):
        self.messages.append((s, 'messages'))

    def warning(self, s):
        self.messages.append((s, 'warnings'))

    def error(self, s):
        self.messages.append((s, 'errors'))

    def onround(self, character):
        print "[DEBUG] Campaign.onround: character: %s" % character.displayname()
        for item in character.inventory_generator():
            if item[1].get('/core/in_use', False):
                self.error('%s is being used' % (item[1].displayname()))
                item[1].onround(player=character)
                if item[0] in character.get('/core/inventory/equiped', {}).keys():
                    print "[DEBUG] Campaign.onround: Equipped update: %s, %s" % (item[0], item[1])
                    character.put('/core/inventory/equiped/%s' % item[0], item[1]())
                else:
                    print "[DEBUG] Campaign.onround: pack update: %s, %s" % (item[0], item[1])
                    character()['core']['inventory'][item[0]][item[2]] = item[1]()
        character.save()
