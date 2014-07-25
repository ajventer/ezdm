from util import save_json
from objects import EzdmObject, event


class Item(EzdmObject):

    def displayname(self):
        return self.get('/core/name', '') or self.get('/name', '')

    def save(self):
        if 'temp' in self():
            del self()['temp']
        name = '%s.json' % self.get('/core/name', '')
        return save_json('items', name.lower().replace(' ', '_'), self.json)

    def slot(self):
        return self.get('/conditional/slot', '')

    def price_tuple(self):
        return (self.get('/core/price/gold', 0), self.get('/core/price/silver', 0), self.get('/core/price/copper', 0))

    def itemtype(self):
        return self.get('/core/type', 'other') or self.get('/type', self(), 'other')

    def onpickup(self, player, page):
        event(self, "/events/onpickup", {'item': self, 'page': page, 'player': player})

    def onequip(self, player, page):
        event(self, "/events/onequip", {'item': self, 'page': page, 'player': player})

    def onuse(self, player, target, page):
        event(self, "/events/onuse", {'item': self, 'page': page, 'player': player, 'target': target})

    def onround(self, player, target, page):
        event(self, "/events/onround", {'item': self, 'page': page, 'player': player, 'target': target})

    def onfinish(self, player, target, page):
        event(self, "/events/onfinish", {'item': self, 'page': page, 'player': player, 'target': target})

    def ondrop(self, player, page):
        event(self, "/events/ondrop", {'item': self, 'page': page, 'player': player})
