from frontend import Session, Page
import frontend
from character import Character
from item import Item
from util import load_json, find_files


class INVENTORY(Session):
    def __init__(self):
        self._character = None
        Session.__init__(self)

    def render(self, requestdata):
        page = Page()
        self._data['detailview'] = None
        if requestdata and 'loadfrom' in requestdata:
            self._character = Character(load_json('characters', requestdata['loadfrom']))
        if frontend.mode == 'campaign' and frontend.campaign:
                self._character = frontend.campaign.current_char()
        self._data['editmode'] = frontend.mode == 'dm'
        if self._data['editmode']:
            loadfrom = {}
            loadfrom['name'] = 'Character'
            loadfrom['keyname'] = 'loadfrom'
            loadfrom['allow_new'] = False
            source = 'characters'
            loadfrom['items'] = find_files(source, '*.json', basename=True, strip='.json')
            page.add('load_defaults_from.tpl', loadfrom)
        if self._character:
            self._data['inventory'] = self._character.get('/core/inventory', {})

            self._data['character'] = self._character.displayname()
            self._data['items'] = find_files('items', '*.json', basename=True, strip='.json')

            if requestdata:
                if 'acquire_item' in requestdata:
                    item = Item(load_json('items', requestdata['acquire_item']))
                    self._character.acquire_item(item)
                if 'selected' in requestdata:
                    print "Item selected"
                    if requestdata['section'] == 'pack':
                        item = Item(self._character.get('/core/inventory/pack', [])[int(requestdata['selected'])])
                        self._data['packindex'] = int(requestdata['selected'])
                        if 'itemslot' in self._data:
                            del(self._data['itemslot'])
                    else:
                        item = Item(self._character.get('/core/inventory/equiped/%s' % requestdata['section'], {}))
                        self._data['itemslot'] = requestdata['section'].strip()
                        if 'packindex' in self._data:
                            del(self._data['packindex'])
                    if self._data['editmode']:
                        item.identify()
                    self._data['detailview'] = item.render()
                if 'dropitem' in requestdata:
                    idx = int(requestdata['pack_index'])
                    self._character.drop_item(idx)
                if 'equipitem' in requestdata:
                    idx = int(requestdata['pack_index'])
                    self._character.equip_item(idx)
                if 'unequipitem' in requestdata:
                    print "Unequiping from %s" % requestdata['slot_name']
                    self._character.unequip_item(requestdata['slot_name'].strip())
                if 'givemoney' in requestdata:
                    gold = int(requestdata['gold'])
                    silver = int(requestdata['silver'])
                    copper = int(requestdata['copper'])
                    self._character.gain_money(gold, silver, copper)

            page.add('inventory.tpl', self._data)
            self._character.save()
        return page.render()
