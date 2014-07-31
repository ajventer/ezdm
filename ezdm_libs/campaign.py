from util import save_json, load_json
from character import Character
from objects import EzdmObject


class Campaign(EzdmObject):

    def __init__(self, json):
        self.json = json
        self.put('/core/current_char', 0)

    def chars_in_round(self):
        chars = self.get('/core/players', [])
        #TODO For each player, find the map he is on, then find any living monsters on the revealed tiles in that map and add them
        return chars

    def current_char(self):
            c = self.get('/core/current_char', 0)
            cname = self.chars_in_round()[c]
            char = Character(load_json('characters', cname))
            return char

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('campaigns', name.lower().replace(' ', '_'), self.json)
