from .frontend import Session, Page, mode
from . import frontend
from .character import Character
from .item import Item
from .util import load_json, find_files, inrange, debug


class SPELLBOOK(Session):
    def __init__(self):
        self._character = None
        Session.__init__(self)

    def render(self, requestdata):
        page = Page()
        self._data['detailview'] = None
        self._data['targetlist'] = list(frontend.campaign.characterlist)
        self._data['editmode'] = mode() == 'dm'
        self._character = frontend.campaign.current_char()
        if self._data['editmode']:
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
        self._data['targetlist'].insert(0, self._character)
        self._data['spells'] = []
        self._data['spell_list'] = []
        for spell in find_files('items', '*.json', basename=True, strip='.json'):
            if Item(load_json('items', spell)).itemtype() == 'spell':
                self._data['spell_list'].append(spell)
        if requestdata:
            if 'sleep' in requestdata:
                self._character.put('/core/inventory/spells_memorized', [])
            if 'memorize_spells' in requestdata:
                memorized = []
                for index in requestdata.getall('memorize_spell'):
                    if index != 'ignoreme':
                        memorized.append(int(index))
                self._character.put('/core/inventory/spells_memorized', memorized)
                debug(memorized)
            if 'learnspell' in requestdata:
                page.message(self._character.learn_spell(Item(load_json('items', requestdata['learnspell']))))
            if 'selected' in requestdata:
                debug("Handling selection")
                json = self._character.get('/core/inventory/spells', [])
                json = json[int(requestdata['selected'])]
                item = Item(json)
                self._data['detailidx'] = int(requestdata['selected'])
                self._data['detailsection'] = requestdata['section']
                self._data['detailview'] = item.render()
            if 'unlearn' in requestdata:
                self._data['detailview'] = None
                self._character.unlearn_spell(int(requestdata['spellindex']))
                page.warning('Spell has been unlearned')
            if 'cast_spell' in requestdata or 'stopcasting' in requestdata or 'teach_spell' in requestdata:
                item = Item(self._character.get('/core/inventory/spells', [])[int(requestdata['pack_index'])])
                target = Character(load_json('characters', requestdata['cast_spell_target']))
                if 'stopcasting' in requestdata:
                    item.interrupt()
                elif 'stopcasting' in requestdata:
                    item.onuse(self._character, target)
                    idx = self._character()['core']['inventory']['spells_memorized'].index(int(requestdata['pack_index']))
                    del (self._character()['core']['inventory']['spells_memorized'][idx])
                    self._character()['core']['inventory']['spells'][int(requestdata['pack_index'])] = item()
                elif 'teach_spell' in requestdata:
                    page.message(target.learn_spell(item))
                    target.autosave()

        self._character.save()
        for spell in self._character.inventory_generator(sections=['spells']):
            self._data['spells'].append(spell)
        self._data['memorized'] = self._character.memorized_spells()
        self._data['character'] = self._character
        classclass = self._character.get('/core/class/class', '')
        classparent = self._character.get('/core/class/parent', '')
        spell_prog = load_json('adnd2e', 'various')["spell progression"]
        found = False
        for key in spell_prog:
            if key == classparent or key == classclass:
                spell_prog = spell_prog[key]
                debug(key)
                found = True
                break
        if found:
            debug("Finding spell progression")
            level = self._character.get('/core/combat/level-hitdice', 1)
            for key in spell_prog:
                if inrange(level, key):
                    spell_prog = spell_prog[key]
                    break
            self._data['spellprog'] = spell_prog
            if 'casting_level' in self._data['spellprog']:
                del(self._data['spellprog']['casting_level'])
        self._data['spelltype'] = list(spell_prog.keys())[0]
        page.add('spellbook.tpl', self._data)

        return page.render()
