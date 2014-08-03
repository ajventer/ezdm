from util import save_json
from objects import EzdmObject, event
import copy


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
            out = copy.deepcopy(self())
            print "Self charges", self().get('/core/charges', '')
            if 'events' in out:
                del(out['events'])
            if 'core' in out:
                if 'charges' in out['core']:
                    if int(out['core']['charges']) == -1:
                        out['core']['charges'] = 'Unlimited'
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

    def onpickup(self, player):
        event(self, "/events/onpickup", {'item': self, 'player': player})

    def onequip(self, player):
        event(self, "/events/onequip", {'item': self, 'player': player})

    def onuse(self, player, target):
        self.put('/core/in_use', True)
        self.put('/core/target', target.name())
        event(self, "/events/onuse", {'item': self, 'player': player, 'target': target})

    def onround(self, player, target):
        if self.get('/core/in_use', False):
            rounds = self.get('/core/rounds_per_charge', 0)
            if rounds > 0:
                rounds -= 1
            self.put('/core/rounds_per_charge', rounds)
            target = target or self.get('/core/target', None)
            if rounds:
                event(self, "/events/onround", {'item': self, 'player': player, 'target': target})
            else:
                self.onfinish(player=player, target=target)

    def onfinish(self, player, target):
        self.put('/core/in_use', False)
        self.put('/core/target', None)
        charges = self.get('/core/charges', 0)
        if charges > 0:
            charges -= 1
            self.put('/core/charges', charges)
        event(self, "/events/onfinish", {'item': self, 'player': player, 'target': target})

    def ondrop(self, player):
        event(self, "/events/ondrop", {'item': self, 'player': player})
