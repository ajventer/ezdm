from frontend import Session, Page
import frontend
from gamemap import GameMap
from util import find_files, load_json
from simplejson import loads
from character import Character
from item import Item
from combat import attack


class MAPS(Session):
    def __init__(self):
        self._character = None
        Session.__init__(self)
        self._map = None

    def inputhandler(self, requestdata, page):
        if 'loadmap' in requestdata and requestdata['loadmap'] == 'New Map':
            self._map = GameMap(name='New Map')
        else:
            if requestdata and 'loadmap' in requestdata and requestdata['loadmap'] != 'New Map':
                self._map = GameMap(json=load_json('maps', '%s.json' % requestdata['loadmap']))
            elif requestdata and 'savemap' in requestdata:
                self._map.put('/name', requestdata['mapname'])
                if 'max_x' in requestdata:
                    self._map = GameMap(name=requestdata['mapname'], max_x=int(requestdata['max_x']), max_y=int(requestdata['max_y']), lightradius=int(requestdata['lightradius']))
                page.message('Map saved as:' + self._map.save())
                frontend.campaign.addmap(self._map.name())
        if requestdata:
            if "clicked_x" in requestdata:
                self._data['zoom_x'] = int(requestdata['clicked_x'])
                self._data['zoom_y'] = int(requestdata['clicked_y'])
            if "loadtilefromfile" in requestdata:
                self._map.load_tile(self._data['zoom_x'], self._data['zoom_y'], '%s.json' % requestdata["load_tile_from_file"])
            if 'pythonconsole' in requestdata:
                exec requestdata['pythonconsole']
            if 'addchartotile' in requestdata:
                self._map.save()
                cname = requestdata['charactername']
                character = Character(load_json('characters', cname))
                character.moveto(self._map.name(), self._data['zoom_x'], self._data['zoom_y'])
                character.autosave()
                self._map = GameMap(load_json('maps', self._map.name()))
            if 'updatejson' in requestdata:
                newjson = loads(requestdata['jsonbox'])
                self._map.load_tile_from_json(self._data['zoom_x'], self._data['zoom_y'], newjson)
            if 'addnpctotile' in requestdata:
                self._map.save()
                cname = requestdata['npcname']
                npc = Character(load_json('characters', cname))
                npc.moveto(self._map.name(), self._data['zoom_x'], self._data['zoom_y'])
                self._map.addtotile(self._data['zoom_x'], self._data['zoom_y'], npc, 'npcs')
                self._map = GameMap(load_json('maps', self._map.name()))
            if 'additemtotile' in requestdata:
                self._map.addtotile(self._data['zoom_x'], self._data['zoom_y'], requestdata['itemname'], 'items')
            if 'removenpcfromtile' in requestdata:
                tile = self._map.tile(self._data['zoom_x'], self._data['zoom_y'])
                npcs = tile.get('/conditional/npcs', [])
                print "NPCs here", npcs
                for npc in npcs:
                    print "Testing npc"
                    n = Character(npc)
                    if n.name() == '%s.json' % requestdata['npcname']:
                        print "    Match"
                        break
                self._map.removefromtile(self._data['zoom_x'], self._data['zoom_y'], n.get_tile_index(), 'npcs')
                self._map.save()
            if 'removeitemfromtile' in requestdata:
                self._map.removefromtile(self._data['zoom_x'], self._data['zoom_y'], requestdata['itemname'], 'items')
            if 'settargetmap' in requestdata:
                target = requestdata['targetmap']
                if not target.endswith('.json'):
                    target = '%s.json' % target
                target_x = int(requestdata['target_x'])
                target_y = int(requestdata['target_y'])
                self._map.tile(self._data['zoom_x'], self._data['zoom_y']).linktarget(target=target, x=target_x, y=target_y)
            if 'movehere' in requestdata:
                self._character.moveto(self._map.name(), self._data['zoom_x'], self._data['zoom_y'])
                self._character.autosave()
                self._map = GameMap(load_json('maps', self._map.name()))
            if "followlink" in requestdata:
                tile = self._map.tile(self._data['zoom_x'], self._data['zoom_y'])
                newmap = tile.get('/conditional/newmap/mapname', '')
                new_x = tile.get('/conditional/newmap/x', 0)
                new_y = tile.get('/conditional/newmap/y', 0)
                self._character.moveto(mapname=newmap, x=new_x, y=new_y, page=page)
                self._character.autosave()
                self._map = GameMap(load_json('maps', newmap))
                self._data['zoom_x'] = new_x
                self._data['zoom_y'] = new_y
            if 'sellitem' in requestdata:
                idx = int(requestdata['itemtosell'])
                self._character.sell_item(idx)
                self._character.autosave()
            if 'iconsection' in requestdata and requestdata['iconsection']:
                print "Processing icon click"
                iconsection = requestdata['iconsection']
                self._data['detailname'] = requestdata['iconname']
                if iconsection == 'money':
                    self._data['detailview'] = {}
                    self._data['detailview']['gold'] = self._map.tile(self._data['zoom_x'], self._data['zoom_y']).get('/conditional/gold', 0)
                    self._data['detailview']['silver'] = self._map.tile(self._data['zoom_x'], self._data['zoom_y']).get('/conditional/silver', 0)
                    self._data['detailview']['copper'] = self._map.tile(self._data['zoom_x'], self._data['zoom_y']).get('/conditional/copper', 0)
                    self._data['detailtype'] = 'item'
                elif iconsection == 'items':
                    i = Item(load_json('items', requestdata['iconname']))
                    if self._map.tile(self._data['zoom_x'], self._data['zoom_y']).tiletype() == 'shop':
                        print "Pre-identifying item from shop"
                        i.identify()
                    self._data['detailview'] = i.render()
                    self._data['detailtype'] = 'item'
            if 'iconindex' in requestdata and requestdata['iconindex']:
                self._data['detailtype'] = 'character'
                target = frontend.campaign.characterlist[int(requestdata['iconindex'])]
                self._data['detailview'] = target.render()
                self._data['detailindex'] = requestdata['iconindex']
            if 'itemdetail' in requestdata:
                del(self._data['detailtype'])
                if requestdata['detailname'] == 'money':
                    moneytuple = self._map.getmoney(self._data['zoom_x'], self._data['zoom_y'])
                    self._character.gain_money(*moneytuple)
                    self._map.putmoney(self._data['zoom_x'], self._data['zoom_y'], 0, 0, 0)
                    page.message('You picked up some money !')
                    self._character.autosave()
                elif requestdata['detailtype'] == 'item':
                    print "Processing item selection"
                    i = Item(load_json('items', requestdata['detailname']))
                    if requestdata['itemdetail'] == 'Pick up':
                        print "Pickin up item"
                        self._character.acquire_item(i)
                        self._map.removefromtile(self._data['zoom_x'], self._data['zoom_y'], requestdata['detailname'], 'items')
                        page.message('You picked up a %s' % requestdata['detailname'])
                    else:
                        print "Buying item"
                        i.identify()
                        self._character.buy_item(i, page=page)
                    self._character.autosave()
            if 'attack' in requestdata:
                attackmods = requestdata.getall('attackmods')
                target = frontend.campaign.characterlist[int(requestdata['detailindex'])]
                attack(self._character, target, attackmods, int(requestdata['custom_tohit']), int(requestdata['custom_dmg']))
                self._map = GameMap(load_json('maps', self._map.name()))
            if 'useitem' in requestdata:
                target = frontend.campaign.characterlist[int(requestdata['detailindex'])]
                idx = int(requestdata['tact_item'])
                item = Item(self._character.get('/core/inventory/pack', [])[idx])
                item.onuse(self._character, target)
                self._character()['core']['inventory']['pack'][idx] = item()
                self._character.autosave()
            if 'castspell' in requestdata:
                target = frontend.campaign.characterlist[int(requestdata['detailindex'])]
                idx = int(requestdata['tact_spell'])
                item = Item(self._character.get('/core/inventory/spells', [])[idx])
                item.onuse(self._character, target)
                del (self._character()['core']['inventory']['spells_memorized'][idx])
                self._character()['core']['inventory']['spells'][idx] = item()
                self._character.autosave()

            if not 'savemap' in requestdata and not 'loadmap' in requestdata and self._data['editmode']:
                page.warning('WARNING: Changes are not yet saved')

    def render(self, requestdata):
        page = Page()
        self._data['zoom_x'] = 0
        self._data['zoom_y'] = 0
        if 'detailview' in self._data:
            del(self._data['detailview'])

        self._data['attackmods'] = load_json('adnd2e', 'attack_mods')
        self._data['editmode'] = frontend.mode == 'dm'
        self._data['campaign'] = frontend.campaign
        self._character = frontend.campaign.current_char()
        if not self._data['editmode']:
            self._data['packitems'] = self._character.for_sale()

        if requestdata:
            self.inputhandler(requestdata, page)
        else:
            if not self._data['editmode']:
                print "reloading map"
                mapname = self._character.get('/core/location/map', '')
                self._map = GameMap(load_json('maps', mapname))
        if self._data['editmode'] and not self._map:
            self._map = GameMap(name='New Map')
        self._data['map'] = self._map()
        self._data['mapobj'] = self._map
        charicons = frontend.campaign.chars_in_round()
        if self._map.name() in charicons:
            self._data['charicons'] = charicons[self._map.name()]
        #elif 'charicons' in self._data:
         #   del (self._data['charicons'])
        self._data['maplist'] = find_files('maps', '*.json', basename=True, strip='.json')
        self._data['tilelist'] = find_files('tiles', '*.json', basename=True, strip='.json')
        charlist = find_files('characters', '*.json', basename=True, strip='.json')
        self._data['playerlist'] = []
        self._data['npclist'] = []
        self._data['itemlist'] = find_files('items', '*.json', basename=True, strip='.json')
        for c in charlist:
            tmpc = Character(load_json('characters', c))
            if tmpc.character_type() == 'player':
                self._data['playerlist'].append(c)
            else:
                self._data['npclist'].append(c)
        self._data['current_char'] = self._character
        added = []
        for idx in self._character.get('/core/inventory/spells_memorized', []):
            added.append(idx)
        added = list(set(added))
        tactical_spells = []
        for idx in added:
            tactical_spells.append((idx, Item(self._character.get('/core/inventory/spells', [])[idx])))
        self._data['tactical_spells'] = tactical_spells
        page.add('map_render.tpl', self._data)
        if not self._data['editmode']:
            self._map.save()
        return page.render()
