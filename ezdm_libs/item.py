from util import save_json
from objects import EzdmObject, event
import copy
import frontend


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
        print "[DEBUG] Item.onuse: player %s, target %s" % (player.displayname(), target.displayname())
        charges = self.get('/core/charges', 0)
        if charges == 0:
            return
        self.put('/core/in_use', True)
        self.put('/core/target', target.index)
        event(self, "/events/onuse", {'item': self, 'player': player, 'target': target})

    def onround(self, player):
        target = self.get('/core/target', 0)
        target = frontend.campaign.characters[target]
        print "[DEBUG] Item.onround: self: %s, player: %s, target: %s" % (self.displayname(), player.displayname(), target)
        if self.get('/core/in_use', False):
            rounds = self.get('/core/rounds_per_charge', 0)
            current_rounds_performed = self.get('/core/current_rounds_performed', 0)
            print "[DEBUG] item.onround: current_rounds_performed: %s, round: %s" % (current_rounds_performed, rounds)
            if current_rounds_performed < rounds:
                current_rounds_performed += 1
            self.put('/core/current_rounds_performed', current_rounds_performed)
            if current_rounds_performed < rounds:
                print "[DEBUG] item.onround: run onround event"
                event(self, "/events/onround", {'item': self, 'player': player, 'target': target})
            else:
                print "[DEBUG] item.onround: running onfinish"
                self.onfinish(player=player)

    def onfinish(self, player):
        target = self.get('/core/target', 0)
        target = frontend.campaign.characters[target]
        self.put('/core/in_use', False)
        self.put('/core/target', None)
        charges = self.get('/core/charges', 0)
        if charges > 0:
            charges -= 1
            self.put('/core/charges', charges)
        self.put('/core/current_rounds_performed', 0)
        event(self, "/events/onfinish", {'item': self, 'player': player, 'target': target})

    def ondrop(self, player):
        event(self, "/events/ondrop", {'item': self, 'player': player})

    def interrupt(self):
        self.put('/core/in_use', False)
        
