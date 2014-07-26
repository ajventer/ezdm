from frontend import Session, Page
from util import load_json, find_files
from character import Character


class XPTOOL(Session):
    character = None

    def render(self, requestdata):
        page = Page()
        clist = []
        for char in find_files('characters', '*.json'):
            clist.append(Character(load_json('characters', char)))
        if requestdata:
            self._data.update(requestdata)
        if 'LoadDefaultFrom' in self._data:
            del(self._data['LoadDefaultFrom'])
        loadform = {'action': '/EZDM_XPTOOL', 'name': 'Character', 'keyname': 'character', 'allow_new': 'False'}
        if not self.character:
            if not 'character' in self._data:
                loadform['items'] = [c.displayname() for c in clist if c.character_type() == 'player']
                page.add('load_defaults_from.tpl', loadform)
                return page.render()
            else:
                self.character = [c for c in clist if c.displayname() == self._data['character']]
                del(self._data['character'])
                if self.character:
                    self.character = self.character[0]
        page.message('Adding XP for %s' % self.character.displayname())
        return page.render()
