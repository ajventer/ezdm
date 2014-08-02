from util import save_json
from objects import EzdmObject, event


class Item(EzdmObject):

    def displayname(self):
        return self.get('/core/name', '') or self.get('/name', '')

    def save(self):
        if 'temp' in self():
            del self()['temp']
        return save_json('items', self.name(), self.json)

    def name(self):
        name = '%s.json' % self.get('/core/name', '')
        return name.lower().replace(' ', '_')

    def slot(self):
        return self.get('/conditional/slot', '')

    def identified(self):
        return self.get('/core/identified', '')

    def render(self):
        if self.identified():
            out = self()
            if 'events' in out:
                del(out['events'])
        else:
            out = {}
            out['core'] = {}
            out['core']['icon'] = self.get('/core/icon', '')
            out['core']['name'] = self.get('/core/name', '')
            out['core']['identified'] = self.get('/core/identified', False)
        return out

    def identify(self):
        self.put('/core/identified', True)

    def price_tuple(self):
        gold = self.get('/core/price/gold', 0)
        silver = self.get('/core/price/silver', 0)
        copper = self.get('/core/price/copper', 0)
        try:
            gold = int(gold)
        except ValueError:
            gold = 0
        try:
            silver = int(silver)
        except ValueError:
            silver = 0
        try:
            copper = int(copper)
        except ValueError:
            copper = 0
        return (gold, silver, copper)

    def itemtype(self):
        return self.get('/core/type', 'other')

    def armortype(self):
        return self.get('/conditional/material', 'plate')

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
