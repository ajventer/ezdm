from .frontend import Session, Page, mode
from . import frontend
from .util import load_json, debug
from .character import Character



class XPTOOL(Session):
    def __init__(self):
        Session.__init__(self)
        self.characters = []

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
                loadform['items'].insert(0, 'campaign')
                loadform['items'].insert(1, frontend.campaign.current_char().name())
                page.add('load_defaults_from.tpl', loadform)
                return page.render()
            else:
                if self._data['character'] == 'frontend.campaign':
                    debug('XP for whole campaign')
                    for character in frontend.campaign.players():
                        self.characters.append(character)
                else:
                    debug('XP For %s' % self._data['character'])
                    self.characters.append(requestdata['character'])

        if self.characters and not 'xp_ammount' in self._data:
            page.message('Adding experience points for %s' % self.characters)
            page.message('current XP/Level: ')
            debug('Character list', self.characters)
            for charname in self.characters:
                if charname == 'frontend.campaign':
                    continue
                character = Character(load_json('characters', charname))
                debug('Character: ' + str(character) + character.displayname())
                page.message('    %s/%s' % (character.get('/core/personal/xp', 0), character.next_level()))
            xpform = {'action': '/EZDM_XPTOOL', 'name': 'Experience Points', 'default_value': 0}
            xpform['question'] = 'How much experience points do you grant ?'
            xpform['inputname'] = 'xp_ammount'
            xpform['submitname'] = 'add_xp'
            xpform['submitvalue'] = 'Give XP'
            page.add('simple_input.tpl', xpform)
            return page.render()
        for charname in self.characters:
            if charname == 'frontend.campaign':
                continue
            character = Character(load_json('characters', charname))
            debug("New XP", character.give_xp(int(self._data['xp_ammount'])))
            character.save()
        self._data = {}
        self.characters = []
        return page.render()
