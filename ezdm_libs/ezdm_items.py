from frontend import Session, Page
from util import find_files


class ITEMS(Session):

    def itemlist(self):
        return find_files('items', '*.json', basename=True, strip='.json')

    def welcomeform(self):
        page = Page()
        select = {}
        select['action'] = '/ITEMS'
        select['name'] = 'Item'
        select['keyname'] = 'item'
        select['items'] = self.itemlist()
        page.add('create_select.tpl', select)
        return page.render()

    def newitemform(self, loadfrom=None):
        page = Page()
        loadfrom = {}
        loadfrom['action'] = '/ITEMS'
        loadfrom['name'] = 'Load Item'
        loadfrom['keyname'] = 'loadfrom'
        loadfrom['items'] = self.itemlist()
        page.add('load_defaults_from.tpl', loadfrom)

        return page.render()

    def render(self, requestdata):
        if requestdata:
            for item in requestdata:
                print requestdata[item]
        if not requestdata:
            print "Welcome form"
            return self.welcomeform()
        if requestdata.get('item').lower() == 'new_item' or self._data.get('action') == 'new item':
            print "New Item form"
            self._data['action'] = 'new item'
            load = 'loadfrom' in requestdata and requestdata['loadfrom'] or None
            return self.newitemform(load)
