from util import save_json
from objects import EzdmObject


class Campaign(EzdmObject):

    def save(self):
        name = '%s.json' % self.get('/core/name', '')
        return save_json('campaigns', name.lower().replace(' ', '_'), self.json)


