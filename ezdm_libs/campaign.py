from .util import save_json, load_json, rolldice, debug
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
        self.initiative = []

    def __charitem(self, character):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> CharacterList()._CharacterList__charitem(char)
        ('player', 'tiny_tim.json')
        """
        if not character:
            return
        if character.character_type() == 'player':
            load_tuple = ('player', character.name())
        else:
            loc = character.location()
            load_tuple = ('npc', loc, character.get_hash())
        character.autosave()
        return load_tuple

    def append(self, character):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> c = CharacterList()
        >>> i = len(c)
        >>> c.append(char) == i
        True
        """
        newindex = len(self.characters)
        self.characters.append(self.__charitem(character))
        return newindex

    def __loaditem(self, load_tuple):
        """
        >>> char = Character(load_json('characters', 'tiny_tim.json'))
        >>> c = CharacterList()
        >>> c.append(char)
        0
        >>> c._CharacterList__loaditem(('player','tiny_tim.json')).displayname()
        '[TINY TIM]'
        """
        if load_tuple[0] == 'player':
            return Character(load_json('characters', load_tuple[1]))
        else:
            loc = load_tuple[1]
            mapname = loc['map']
            x = loc['x']
            y = loc['y']
            gamemap = GameMap(load_json('maps', mapname))
            tile = gamemap.tile(x, y)
            npcs_here = tile.get('/conditional/npcs', {})
            for npc in npcs_here:
                npcjson = npcs_here[npc]
                npc = Character(npcjson)
                if npc.get_hash() == load_tuple[2]:
                    return npc

    def __list__(self):
        """
        >>> c = CharacterList()
        >>> c.append(Character(load_json('characters','tiny_tim.json')))
        0
        >>> c.append(Character(load_json('characters','bardic_rogue.json')))
        1
        >>> list(c)
        [<ezdm_libs.character.Character object at ...>, <ezdm_libs.character.Character object at ...>]

        """
        tempchars = []
        for load_tuple in self.characters:
            tempchars.append(self.__loaditem(load_tuple))
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
        >>> c.append(Character(load_json('characters', 'tiny_tim.json')))
        0
        >>> c[0]
        <ezdm_libs.character.Character object at ...>
        >>> c[0].displayname() == Character(load_json('characters', 'tiny_tim.json')).displayname()
        True

        """
        if not isinstance(key, int):
            raise TypeError('Index must be integer')
        load_tuple = self.characters[key]
        return self.__loaditem(load_tuple)

    def index(self, key):
        return self.characters.index(self.__charitem(key))
        

    def __setitem__(self, key, value):
        """
        >>> c = CharacterList()
        >>> c.append(Character(load_json('characters','bardic_rogue.json')))
        0
        >>> c[0] = Character(load_json('characters', 'tiny_tim.json'))
        >>> c[0].displayname()
        '[TINY TIM]'
        """
        self.characters[key] = self.__charitem(value)

    def __delitem__(self, key):
        """
        >>> c = CharacterList()
        >>> len(c)
        0
        >>> i = c.append(Character(load_json('characters', 'bardic_rogue.json')))
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
        >>> ch = Character(load_json('characters','tiny_tim.json'))
        >>> c.append(ch)
        0
        >>> ch in c
        True
        >>> ch = Character(load_json('characters','bardic_rogue.json'))
        >>> ch in c
        False
        """
        tocheck = self.__charitem(item)
        return tocheck in self.characters


class Campaign(EzdmObject):
    """
    >>> json = load_json('campaigns','test_campaign.json')
    >>> campaign = Campaign(json)
    >>> campaign()['core']['name']
    'Test Campaign'
    """

    def __init__(self, json):
        """
        >>> json = load_json('campaigns','test_campaign.json')
        >>> campaign = Campaign(json)
        >>> campaign.messages == []
        True
        """

        self.characterlist = CharacterList()
        self.json = json
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
        >>> json = load_json('campaigns','test_campaign.json')
        >>> campaign = Campaign(json)
        >>> campaign.players()
        ['wizard_mage.json', 'tiny_tim.json', 'bardic_rogue.json']
        """
        return self.get('/core/players', [])

    def chars_in_round(self):
        """
        >>> json = load_json('campaigns','test_campaign.json')
        >>> campaign = Campaign(json)
        >>> isinstance(campaign.chars_in_round(), dict)
        True
        """
        icons = {}
        self.playermaps = []
        self.characterlist = CharacterList()
        players = self.players()
        for player in sorted(players):
            if not player.endswith('.json'):
                player = '%s.json' % player
            p = Character(load_json('characters', player))
            if p.get('/core/combat/hitpoints', 0) > 0:
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
        for mapname in self.get('/core/maps', []):
            if not mapname in icons:
                continue
                #icons[mapname] = {}
            gamemap = GameMap(load_json('maps', mapname))
            for y in range(0, gamemap.get('/max_y', 1)):
                for x in range(0, gamemap.get('/max_x', 1)):
                    tile = gamemap.tile(x, y)
                    if not (x, y) in icons[mapname]:
                        icons[mapname][(x, y)] = []
                    if tile.revealed():
                        npcs_here = tile.get('/conditional/npcs', {})
                        if isinstance(npcs_here, list):
                            continue
                        for npc in npcs_here:
                            n = Character(npcs_here[npc])
                            if n.get('/core/combat/hitpoints', 1) > 0:
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
        >>> json = load_json('campaigns','test_campaign.json')
        >>> campaign = Campaign(json)
        >>> campaign.current_char()
        <ezdm_libs.character.Character object at ...>
        """
        # if len(self.characterlist) == 0:
        #     self.error('All players are dead !')
        #     self.error('Here comes the resurrection fairy !')
        #     for player in self.players():
        #         char = Character('characters', player)
        #         char.put('/core/combat/hitpoints', 1)
        #         char.save()
        #     self.chars_in_round()
        return self.characterlist[self.current]

    def endround(self):
        pass

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
        self.error("Campaign.onround: player=%s, %s" % (character.displayname(), character.autosave()))
