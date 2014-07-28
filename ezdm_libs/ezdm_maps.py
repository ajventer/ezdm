from frontend import Session, Page
from map import Map
import pprint


class MAPS(Session):
    def render(self, requestdata):
        page = Page()
        if not requestdata:
            self._map = Map(name='New Map')
        self._map.load_tile(1, 1, 'rock_wall.json')
        pprint.pprint(self._map())
        page.add('map_render.tpl', self._map())
        return page.render()
