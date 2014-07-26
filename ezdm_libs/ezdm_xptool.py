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
        page.message('Adding experience points for %s' % self.character.displayname())
        page.message('current XP/Level: %s/%s' % (self.character.get('/core/personal/xp', 0), self.character.next_level()))
        if not 'xp_ammount' in self._data:
            xpform = {'action': '/EZDM_XPTOOL', 'name': 'Experience Points', 'default_value': 0}
            xpform['question'] = 'How much experience points do you grant ?'
            xpform['inputname'] = 'xp_ammount'
            xpform['submitname'] = 'add_xp'
            xpform['submitvalue'] = 'Give XP to %s' % self.character.displayname()
            page.add('simple_input.tpl', xpform)
            return page.render()
        print "New XP", self.character.give_xp(int(self._data['xp_ammount']), page)
        self.character.save()
        self.character = None
        self._data = {}
        return page.render()
