import os
from .util import rolldice, debug
from .character import Character
from .gamemap import GameMap
from .objects import EzdmObject


class CharacterList(object):
    """
    >>> c = CharacterList()
    >>> c
    <ezdm_libs.campaign.CharacterList object...>
    """
    characters = []

    def __init__(self):
        self.characters = []

    def append(self, character):
        """
        >>> char = Character('characters/tiny_tim')
        >>> c = CharacterList()
        >>> i = len(c)
        >>> c.append(char) == i
        True
        """
        newindex = len(self.characters)
        self.characters.append(character.key)
        return newindex

    def __list__(self):
        """
        >>> c = CharacterList()
        >>> c.append(Character('characters/tiny_tim'))
        0
        >>> c.append(Character('characters/bardic_rogue'))
        1
        >>> list(c)
        [<ezdm_libs.character.Character object at ...>, <ezdm_libs.character.Character object at ...>]

        """
        tempchars = []
        for key in self.characters:
            tempchars.append(Character(key))
        return tempchars

    def __len__(self):
        """
        >>> len(CharacterList())
        0
        """
        return len(self.characters)

    def __getitem__(self, key):
        """
        >>> c = CharacterList()
        >>> c.append(Character('characters/tiny_tim'))
        0
        >>> c[0]
        <ezdm_libs.character.Character object at ...>
        >>> c[0].displayname() == Character('characters/tiny_tim').displayname()
        True

        """
        if not isinstance(key, int):
            raise TypeError('Index must be integer')
        return Character(self.characters[key])

    def index(self, key):
        """
        >>> c = CharacterList()
        >>> x = Character('characters/tiny_time')
        >>> i = c.append(x)
        >>> i == c.index(x)
        True
        >>> i == c.index(x.key)
        True
        """
        if not isinstance(key, str):
            key = key.key
        try:
            return self.characters.index(key)
        except:
            return -1

    def __setitem__(self, key, value):
        """
        >>> c = CharacterList()
        >>> c.append(Character('characters/bardic_rogue'))
        0
        >>> c[0] = Character('characters/tiny_tim')
        >>> c[0].displayname()
        '[TINY TIM]'
        """
        self.characters[key] = value.key

    def __delitem__(self, key):
        """
        >>> c = CharacterList()
        >>> len(c)
        0
        >>> i = c.append(Character('characters/bardic_rogue'))
        >>> i
        0
        >>> len(c)
        1
        >>> del(c[i])
        >>> len(c)
        0
        """
        if not isinstance(key, int):
            raise TypeError('Index must be an integer')
        if key > len(self.characters) - 1:
            raise ValueError('Index out of range')
        del(self.characters[key])

    def __contains__(self, item):
        """
        >>> c = CharacterList()
        >>> ch = Character('characters/tiny_tim')
        >>> c.append(ch)
        0
        >>> ch in c
        True
        >>> ch = Character('characters/bardic_rogue')
        >>> ch in c
        False
        """
        tocheck = item.key
        return tocheck in self.characters


class Campaign(EzdmObject):
    """
    >>> campaign = Campaign('campaigns/test_campaign')
    >>> campaign()['core']['name']
    'Test Campaign'
    """

    def __init__(self, key):
        """
        >>> campaign = Campaign('campaigns/test_campaign')
        >>> campaign.messages == []
        True
        """
        EzdmObject.__init__(key)
        self.characterlist = CharacterList()
        self.initiative = []
        self.current = self.get('/core/current_char', -1)
        self.messages = []
        self.chars_in_round()

    def real(self):
        return True

    def addmap(self, mapname):
        maps = self.get('/core/maps', [])
        if not isinstance(maps, list):
            maps = []
        maps.append(mapname)
        self.json['core']['maps'] = list(set(maps))
        self.save()

    def players(self):
        """
        >>> campaign = Campaign('campaigns/test_campaign')
        >>> campaign.players()
        ['wizard_mage.json', 'tiny_tim.json', 'bardic_rogue.json']
        """
        return self.get('/core/players', [])

    def chars_in_round(self, editmode=False):
        """
        >>> campaign = Campaign('campaigns/test_campaign')
        >>> isinstance(campaign.chars_in_round(), dict)
        True
        """
        icons = {}
        self.playermaps = []
        npcmaps = []
        self.characterlist = CharacterList()
        players = self.players()
        for player in sorted(players):
            p = Character(os.path.join('characters', player))
            p_idx = self.characterlist.append(p)
            loc = p.location()
            if 'map' in loc:
                mapname = loc['map']
                if not mapname in icons:
                    icons[mapname] = {}
                if not (loc['x'], loc['y']) in icons[mapname]:
                    icons[mapname][(loc['x'], loc['y'])] = []
                icons[mapname][(loc['x'], loc['y'])].append(p_idx)
                self.playermaps.append(mapname)
        for mapname in self.playermaps:
            npckey = mapname
            if not mapname in npcmaps:
                npcmaps.append(mapname)
                gamemap = GameMap(os.path.join('maps', mapname))
                for y in range(0, gamemap.get('/max_y', 1)):
                    npckey = os.path.join(npckey, str(y))
                    for x in range(0, gamemap.get('/max_x', 1)):
                        npckey = os.path.join(npckey, x)
                        tile = gamemap.tile(x, y)
                        if not (x, y) in icons[mapname]:
                            icons[mapname][(x, y)] = []
                        if tile.revealed() or editmode:
                            npcs_here = tile.get('/conditional/npcs', {})
                            if isinstance(npcs_here, list):
                                continue
                            for npc in npcs_here:
                                npckey = os.path.join(npckey, npc)
                                n = Character(npckey)
                                if n.get('/core/combat/hitpoints', 1) > 0 and not n in self.characterlist:
                                    n.put('/core/location', {"map": mapname, "x": x, "y": y})
                                    n_idx = self.characterlist.append(n)
                                    if not (x, y) in icons[mapname]:
                                        icons[mapname][(x, y)] = []
                                    icons[mapname][(x, y)].append(n_idx)
        return icons

    def roll_for_initiative(self):
        initiative = []
        self.initiative = []
        self.message('Rolling for initiative:')
        for char in list(self.characterlist):
            roll = rolldice(numdice=1, numsides=20, modifier=0)
            self.message('%s %s' % (char.displayname(), roll[1]))
            initiative.append((roll[0], char.index))
        for char in sorted(initiative, reverse=True):
            self.initiative.append(char[1])
        self.message('%s rolled the highest and goes first' % self.characterlist[0].displayname())

    def endturn(self):
        self.error('End of turn. Starting new turn.')
        self.chars_in_round()
        #self.roll_for_initiative()

    def current_char(self):
        """
        >>> campaign = Campaign('campaigns/test_campaign')
        >>> campaign.current_char()
        <ezdm_libs.character.Character object at ...>
        """
        c = self.characterlist[self.current]
        if not c:
            self.chars_in_round()
            c = self.characterlist[self.current]
        if not c:
            c = self.characterlist[-1]
        return c

    def endround(self):
        pass

    def message(self, s):
        self.messages.append((s, 'messages'))

    def warning(self, s):
        self.messages.append((s, 'warnings'))

    def error(self, s):
        self.messages.append((s, 'errors'))

    def onround(self, character):
        debug("[DEBUG] Campaign.onround: character: %s" % character.displayname())
        for item in character.inventory_generator():
            if item[1].get('/core/in_use', False):
                self.error('%s is being used' % (item[1].displayname()))
                item[1].onround(player=character)
                if item[0] in list(character.get('/core/inventory/equiped', {}).keys()):
                    debug("[DEBUG] Campaign.onround: Equipped update: %s, %s" % (item[0], item[1]))
                    character.put('/core/inventory/equiped/%s' % item[0], item[1]())
                else:
                    debug("[DEBUG] Campaign.onround: pack update: %s, %s" % (item[0], item[1]))
                    character()['core']['inventory'][item[0]][item[2]] = item[1]()
