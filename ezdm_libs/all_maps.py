from frontend import Session, Page
import frontend
from game_map import GameMap
from util import find_files, load_json


class MAPS(Session):
    def render(self, requestdata):
        page = Page()
        print frontend.mode
        self._data['editmode'] = frontend.mode == 'dm'
        if (not requestdata and self._data['editmode']) or ('loadmap' in requestdata and requestdata['loadmap'] == 'New Map'):
            self._map = GameMap(name='New Map')
        else:
            if 'loadmap' in requestdata and requestdata['loadmap'] != 'New Map':
                self._map = GameMap(json=load_json('maps', '%s.json' % requestdata['loadmap']))
            elif 'savemap' in requestdata:
                self._map.put('/name', requestdata['mapname'])
                if 'max_x' in requestdata:
                    self._map = GameMap(name=requestdata['mapname'], max_x=int(requestdata['max_x']), max_y=int(requestdata['max_y']))
                page.message('Map saved as:' + self._map.save())
        self._data['map'] = self._map()
        self._data['maplist'] = find_files('maps', '*.json', basename=True, strip='.json')
        self._data['maplist'].insert(0, 'New Map')
        page.add('map_render.tpl', self._data)
        return page.render()
