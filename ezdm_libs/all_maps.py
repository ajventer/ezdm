from frontend import Session, Page
import frontend
from gamemap import GameMap
from util import find_files, load_json
from character import Character


class MAPS(Session):
    def render(self, requestdata):
        page = Page()
        self._data['zoom_x'] = 0
        self._data['zoom_y'] = 0

        self._data['editmode'] = frontend.mode == 'dm'
        if (not requestdata and self._data['editmode']) or (requestdata and 'loadmap' in requestdata and requestdata['loadmap'] == 'New Map'):
            self._map = GameMap(name='New Map')
        else:
            if requestdata and 'loadmap' in requestdata and requestdata['loadmap'] != 'New Map':
                self._map = GameMap(json=load_json('maps', '%s.json' % requestdata['loadmap']))
            elif requestdata and 'savemap' in requestdata:
                self._map.put('/name', requestdata['mapname'])
                if 'max_x' in requestdata:
                    self._map = GameMap(name=requestdata['mapname'], max_x=int(requestdata['max_x']), max_y=int(requestdata['max_y']))
                page.message('Map saved as:' + self._map.save())
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
                character.save()
                self._map = GameMap(load_json('maps', self._map.name()))
                self._data['savemap'] = 'Save'
            if 'addnpctotile' in requestdata:
                self._map.addtotile(self._data['zoom_x'], self._data['zoom_y'], requestdata['npcname'], 'npcs')
            if 'additemtotile' in requestdata:
                self._map.addtotile(self._data['zoom_x'], self._data['zoom_y'], requestdata['itemname'], 'items')
            if not 'savemap' in requestdata and not 'loadmap' in requestdata:
                page.warning('WARNING: Changes are not yet saved')

        self._data['map'] = self._map()
        self._data['mapobj'] = self._map
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
        print self._data['tilelist']
        self._data['maplist'].insert(0, 'New Map')
        page.add('map_render.tpl', self._data)
        return page.render()
