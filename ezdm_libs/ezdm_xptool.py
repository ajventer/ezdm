from frontend import Session, Page, JSON_Editor
from util import load_json
from character import Character


class XPTOOL(Session):
    character = None

    def render(self, requestdata):
        page = Page()
        if requestdata:
            self._data.update(requestdata)
        if not self.character:
            if not 'character' in self._data:
                J = JSON_Editor()
                J._name = 'character'
                page.add(*J._loadform(new=False))
                return page.render()
            else:
                self.character = Character(load_json('characters', '%s.json' % self._data['character']))
        page.message('Adding XP for %s' % self.character.displayname())
        return page.render()
