from frontend import Session, Page
from util import find_files, template_dict, json_editor, readfile


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

    def newitemform(self, default=None):
        page = Page()
        loadfrom = {}
        loadfrom['action'] = '/ITEMS'
        loadfrom['name'] = 'Load Item'
        loadfrom['keyname'] = 'loadfrom'
        loadfrom['items'] = self.itemlist()
        page.add('load_defaults_from.tpl', loadfrom)
        print 'Loadform', loadfrom
        if default:
            defaults = readfile('items', '%s.json' % default, json=True)
        else:
            defaults = {}
        template = readfile('adnd2e', 'template_item.json', json=True)
        tpldict = template_dict(template, defaults)
        page.add('json_editor.tpl', json_editor(tpldict, 'New Item', '/ITEMS'))

        return page.render()

    def render(self, requestdata):
        if not requestdata:
            return self.welcomeform()
        if requestdata.get('item', '').lower() == 'new_item' or self._data.get('action') == 'new item':
            self._data['action'] = 'new item'
            load = 'loadfrom' in requestdata and requestdata['loadfrom'] or None
            return self.newitemform(load)
