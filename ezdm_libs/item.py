from util import save_json, readkey, writekey
from objects import EzdmObject


class Item(EzdmObject):

    def displayname(self):
        return self.get('/core/name', '') or self.get('/name', '')

    def save(self):
        if 'temp' in self():
            del self()['temp']
        name = '%s.json' % self.get('/core/name', '')
        print "Saving ",name
        return save_json('items', name.lower().replace(' ','_'), self.json)

    def slot(self):
        return self.get('/conditional/slot', '')

    def itemtype(self):
        return self.get('/core/type', 'other') or self.get('/type', self(), 'other')

    def _event(self, key, localvars):
        code = self.get(key, '')
        if code:
            exec code in {}, localvars

    def onpickup(self, player, page):
        self._event("/events/onpickup", {'item': self, 'page': page, 'player': player})

    def onequip(self, player, page):
        self._event("/events/onequip", {'item': self, 'page': page, 'player': player})

    def onuse(self, player, target, page):
        self._event("/events/onuse", {'item': self, 'page': page, 'player': player, 'target': target})

    def onround(self, player, target, page):
        self._event("/events/onround", {'item': self, 'page': page, 'player': player, 'target': target})

    def onfinish(self, player, target, page):
        self._event("/events/onfinish", {'item': self, 'page': page, 'player': player, 'target': target})

    def ondrop(self, player, page):
        self._event("/events/ondrop", {'item': self, 'page': page, 'player': player})
