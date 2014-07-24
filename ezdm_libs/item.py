from util import save_json, readkey, writekey


class Item:
    json = {}

    def __init__(self, json):
        self.json = json

    def __call__(self):
        return self.json

    def get(self, key, default=None):
        return readkey(key, self(), default)

    def put(self, key, value):
        writekey(key, value, self.json)
        self.save()

    def filename(self, extension="json"):
        if extension:
            return "%s.%s" % (self.json['name'].replace(' ', '_'), extension)
        else:
            return "%s" % (self.json['name'].replace(' ', '_'))

    def save(self):
        save_json('items', self.filename(), self.json)

    def displayname(self):
        return self.get('/core/name', '') or self.get('/name', '')

    def itemtype(self):
        return self.get('/core/type', 'other') or self.get('/type', self(), 'other')

    def _event(self, key, *args):
        python = self.get('/events/%s' % key, '')
        if python:
            exec python in {}, locals

    def onpickup(self, player, page):
        self._event("/events/__Tonpickup_player", {'item': self, 'page': page, 'player': player})

    def onequip(self, player, page):
        self._event("/events/__Tonequip_player", {'item': self, 'page': page, 'player': player})

    def onuse(self, player, target, page):
        self._event("/events/__Tonuse_player_target", {'item': self, 'page': page, 'player': player, 'target': target})

    def onround(self, player, target, page):
        self._event("/events/__Tonround_player_target", {'item': self, 'page': page, 'player': player, 'target': target})

    def onfinish(self, player, target, page):
        self._event("/events/__Tonfinish_player_target", {'item': self, 'page': page, 'player': player, 'target': target})

    def ondrop(self, player, page):
        self._event("/events/__Tondrop_player", {'item': self, 'page': page, 'player': player})
