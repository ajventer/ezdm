from frontend import Session, Page
import frontend
from character import Character
from item import Item
from util import load_json, find_files, debug, price_in_copper


class INVENTORY(Session):
    def __init__(self):
        self._character = None
        Session.__init__(self)

    def render(self, requestdata):
        page = Page()
        self._data['detailview'] = None
        self._data['targetlist'] = list(frontend.campaign.characterlist)
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
            self._data['targetlist'].insert(0, self._character)
            self._data['inventory'] = self._character.get('/core/inventory', {})

            self._data['character'] = self._character.displayname()
            itemlist = find_files('items', '*.json', basename=True, strip='.json')
            self._data['items'] = []
            for item in itemlist:
                    self._data['items'].append(item)

            if requestdata:
                if 'acquire_item' in requestdata:
                    item = Item(load_json('items', requestdata['acquire_item']))
                    num_items = int( requestdata['num_new_items'])
                    for i in range(0,num_items):
                        self._character.acquire_item(item)
                if 'selected' in requestdata:
                    debug("Item selected")
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
                    self._data['detailview'] = item
                if 'sellitem' in requestdata:
                    buyer = Character(load_json('characters', requestdata['buyer']))
                    g = int(requestdata['price_in_gold'])
                    s = int(requestdata['price_in_silver'])
                    c = int(requestdata['price_in_copper'])
                    idx = int(requestdata['pack_index'])
                    item = Item(self._character.get('/core/inventory/pack', [])[idx])
                    self._character.sell_item(itemname=idx, buyer=buyer, gold=g, silver=s, copper=c)
                    page.message('%s sold %s to %s' % (self._character.displayname(), item.displayname(), buyer.displayname()))
                if 'sendmoney' in requestdata:
                    recipient = Character(load_json('characters', requestdata['recipient']))
                    g = int(requestdata['gold'])
                    s = int(requestdata['silver'])
                    c = int(requestdata['copper'])
                    total = price_in_copper(g, s, c)
                    mymoney = price_in_copper(*self._character.money_tuple())
                    if total <= mymoney:
                        recipient.gain_money(g, s, c)
                        recipient.save()
                        self._character.spend_money(g, s, c)
                        page.message('You have sent %s gold, %s silver and %s copper to %s' % (g, s, c, recipient.displayname()))
                    else:
                        page.error('ERROR:You cannot give away more money than you have')

                if 'dropitem' in requestdata:
                    idx = int(requestdata['pack_index'])
                    self._character.drop_item(idx)
                if "learnspell" in requestdata:
                    idx = int(requestdata['pack_index'])
                    spellitem = Item(self._character.get('/core/inventory/pack', [])[idx])
                    page.message(self._character.learn_spell(spellitem))
                    self._character.drop_item(idx)
                if 'equipitem' in requestdata:
                    idx = int(requestdata['pack_index'])
                    result = self._character.equip_item(idx)
                    if not result[0]:
                        page.error('ERROR: %s' % result[1])
                if 'unequipitem' in requestdata:
                    debug("Unequiping from %s" % requestdata['slot_name'])
                    self._character.unequip_item(requestdata['slot_name'].strip())
                if 'useitem' in requestdata or 'stopusing' in requestdata:
                    if 'pack_index' in requestdata:
                        section = 'pack'
                        item = Item(self._character.get('/core/inventory/pack', [])[int(requestdata['pack_index'])])
                    else:
                        section = 'equiped'
                        item = Item(self._character.get('/core/inventory/equiped/%s' % requestdata['slot_name'], {}))
                    debug("Using item: Player: %s, item: %s" % (self._character.displayname(), item.displayname()))
                    target = Character(load_json('characters', requestdata['useitem_target']))
                    if 'useitem' in requestdata:
                        item.onuse(self._character, target)
                    elif 'stopusing' in requestdata:
                        item.interrupt()
                    if section == 'equiped':
                        self._character.put('/core/inventory/%s/%s' % (section, requestdata['slot_name']), item())
                    else:
                        self._character()['core']['inventory']['pack'][int(requestdata['pack_index'])] = item()

                if 'givemoney' in requestdata:
                    gold = int(requestdata['gold'])
                    silver = int(requestdata['silver'])
                    copper = int(requestdata['copper'])
                    self._character.gain_money(gold, silver, copper)
                if 'spendmoney' in requestdata:
                    gold = int(requestdata['gold'])
                    silver = int(requestdata['silver'])
                    copper = int(requestdata['copper'])
                    self._character.spend_money(gold, silver, copper)                    

            page.add('inventory.tpl', self._data)
            self._character.save()
        return page.render()
