from frontend import Session, Page
import frontend
from character import Character
from item import Item
from util import load_json, find_files


class SPELLBOOK(Session):
    def __init__(self):
        self._character = None
        Session.__init__(self)

    def render(self, requestdata):
        page = Page()
        self._data['editmode'] = frontend.mode == 'dm'
        if not self._data['editmode']:
            self._character = frontend.campaign.current_char()
        else:
            loadfrom = {}
            loadfrom['name'] = 'Character'
            loadfrom['keyname'] = 'loadfrom'
            loadfrom['allow_new'] = False
            source = 'characters'
            loadfrom['items'] = find_files(source, '*.json', basename=True, strip='.json')
            page.add('load_defaults_from.tpl', loadfrom)
        if requestdata:
            if 'loadfrom' in requestdata:
                self._character = Character(load_json('characters', requestdata['loadfrom']))
        if not self._character:
            return page.render()
        self._data['spells'] = []
        self._data['spell_list'] = []
        for spell in find_files('items', '*.json', basename=True, strip='.json'):
            if Item(load_json('items', spell)).itemtype() == 'spell':
                self._data['spell_list'].append(spell)
        if requestdata:
            if 'learnspell' in requestdata:
                self._character.learn_spell(Item(load_json('items', requestdata['learnspell'])))
                page.message('Learned a new spell')
            if 'selected' in requestdata:
                print "Handling selection"
                json = self._character.get('/core/inventory/spells', [])
                json = json[int(requestdata['selected'])]
                item = Item(json)
                self._data['detailidx'] = int(requestdata['selected'])
                self._data['detailview'] = item.render()
            if 'unlearn' in requestdata:
                self._data['detailview'] = None
                self._character.unlearn_spell(int(requestdata['spellindex']))
                page.warning('Spell has been unlearned')

            self._character.save()
        for spell in self._character.inventory_generator(sections=['spells']):
            self._data['spells'].append(spell)
        page.add('spellbook.tpl', self._data)

        return page.render()
