from frontend import Session, Page
from util import load_json
from character import Character
import frontend


class XPTOOL(Session):
    characters = []

    def render(self, requestdata):
        page = Page()
        if requestdata:
            self._data.update(requestdata)
        if 'LoadDefaultFrom' in self._data:
            del(self._data['LoadDefaultFrom'])
        loadform = {'action': '/EZDM_XPTOOL', 'name': 'Character', 'keyname': 'character', 'allow_new': 'False'}
        if not self.characters:
            if not 'character' in self._data:
                loadform['items'] = frontend.campaign.players()
                loadform['items'].insert(0, 'Campaign')
                loadform['items'].insert(1, frontend.campaign.current_char().name())
                page.add('load_defaults_from.tpl', loadform)
                return page.render()
            else:
                if self._data['character'] == 'Campaign':
                    for character in frontend.campaign.players():
                        self.characters.append(Character(load_json('characters', character)))
                else:
                    self.characters.append(Character(load_json('characters', self._data['character'])))
        for character in self.characters:
            page.message('Adding experience points for %s' % character.displayname())
            page.message('current XP/Level: %s/%s' % (character.get('/core/personal/xp', 0), character.next_level()))
            if not 'xp_ammount' in self._data:
                xpform = {'action': '/EZDM_XPTOOL', 'name': 'Experience Points', 'default_value': 0}
                xpform['question'] = 'How much experience points do you grant ?'
                xpform['inputname'] = 'xp_ammount'
                xpform['submitname'] = 'add_xp'
                xpform['submitvalue'] = 'Give XP to %s' % character.displayname()
                page.add('simple_input.tpl', xpform)
                return page.render()
            print "New XP", self.character.give_xp(int(self._data['xp_ammount']), page)
            character.save()
        self._data = {}
        self.characters = []
        return page.render()
