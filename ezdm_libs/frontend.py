from jinja2 import Template
from objects import EzdmObject
from util import readfile, find_files, template_dict, json_editor, save_json, list_icons, inflate


class Session:
    def __init__(self):
        self._data = {}

    def read(self):
        return self._data

    def write(self, data):
        self._data = data

    def addkey(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def destroy(self):
        """
        Call this on your final screen to reset the session
        """
        self._data = {}

    def render(self, requestdata):
        """
        This is the function pretty much every child will need to overwrite completely
        """
        page = Page()
        self._data['request'] = requestdata
        page.add('blank.tpl', self._data)
        return page.render()

    def view(self, item):
        """
        Override this with a method to read-only view an item of data
        """
        self.render(item)


class Page:
    def __init__(self, title=None):
        self._sidebar = ''
        self._messages = {'messages': [], 'warnings': [], 'errors': []}
        title = title or 'EZDM'
        menuitems = find_files('', 'ezdm*.py', basename=True)
        menuitems = [m.replace('ezdm_', '').replace('.py', '').upper() for m in menuitems]
        self._menuitems = {'menuitems': menuitems}

        self.content = [('header.tpl', {'title': title}), ('menubar.tpl', self._menuitems)]

    def _has_message(self):
        return self._messages['messages'] or self._messages['warnings'] or self._messages['errors']

    def _add_message(self, message, msgtype):
        self._messages[msgtype].append(message)

    def message(self, message):
        self._add_message(message, 'messages')

    def warning(self, warning):
        self._add_message(warning, 'warnings')

    def sidebar(self, content=''):
        self._sidebar = content

    def error(self, error):
        self._add_message(error, 'errors')

    def tplrender(self, name, data):
        tpl = Template(readfile('templates', name))
        return tpl.render(data)

    def add(self, template, data):
        self.content.append((template, data))

    def render(self):
        if not ('footer.tpl', {}) in self.content:
            self.content.append(('menubar.tpl', self._menuitems))
            self.content.append(('footer.tpl', {}))
        if self._has_message():
            self.content.insert(2, ('messagebox.tpl', self._messages))
        if self._sidebar:
            self.content.insert(2, ('sidebar_top.tpl', {}))
            self.content.insert(-2, ('sidebar.tpl', {'content': self._sidebar}))
        page_content = ''
        for item in self.content:
            page_content += self.tplrender(item[0], item[1])
        return page_content


class JSON_Editor(Session):

    _name = 'X'
    _sidebar = ''

    def __init__(self):
        self._obj = EzdmObject({})
        Session.__init__(self)

    def _loadform(self, new=True):
        loadfrom = {}
        loadfrom['action'] = '/%sS' % self._name.upper()
        loadfrom['name'] = self._name
        loadfrom['keyname'] = 'loadfrom'
        if new:
            loadfrom['allow_new'] = 'True'
        source = '%ss' % self._name
        loadfrom['items'] = find_files(source, '*.json', basename=True, strip='.json')
        return ('load_defaults_from.tpl', loadfrom)

    def sidebar(self, content):
        self._sidebar = content

    def welcomeform(self):
        page = Page()
        lf = self._loadform(True)
        page.add(lf[0], lf[1])
        ilist = {'list': [], 'name': self._name}
        for f in find_files('%ss' % self._name, '*.json', basename=True, strip='.json'):
            ilist['list'].append('<a href=/view/%sS/%s.json>%s</a>' % (self._name.upper(), f, f))
        page.add('list_viewer.tpl', ilist)

        return page.render()

    def newform(self):
        page = Page()
        self.sidebar(page.tplrender('icon_selecter.tpl', list_icons(self._data.get('icon', ''))))
        lf = self._loadform(False)
        page.add(lf[0], lf[1])
        default = self._data.get('loadfrom', None)
        if default and not default == 'New %s' % self._name:
            defaults = readfile('%ss' % self._name, '%s.json' % default, json=True)
            self._data.update(defaults)
        if 'loadfrom' in self._data:
            del(self._data['loadfrom'])
        template = readfile('adnd2e', 'template_%s.json' % self._name, json=True)
        tpldict = template_dict(template, self._data)
        page.add('json_editor.tpl', json_editor(tpldict, 'New %s' % self._name, '/%sS' % self._name.upper()))
        inflated = inflate(self._data)
        if 'core' in inflated:
            duplicate_keys = [k for k in inflated if k in inflated['core']]
            for key in duplicate_keys:
                    del(self._data[key])
            if "save_changes" in self._data and [k for k in self._data if k.startswith('conditional')]:
                del(self._data['save_changes'])
                self._obj.update(self._data)
                page.message('%s saved to %s' % (self._name, self._obj.save()))
                self.destroy()
        if self._sidebar:
            page.sidebar(self._sidebar)
        return page.render()

    def render(self, requestdata):
        if not requestdata:
            return self.welcomeform()
        self._data.update(requestdata)
        return self.newform()

    def view(self, item):
        page = Page()
        page.message(item)
        if not item:
            page.error('No item specified')
            return page.render()
        try:
            print 'try %s' % self._name
            json = readfile('%ss' % self._name, item, json=True)
        except:
            print 'except'
            page.error('No files matching %s found in %s' % (item, self._name))
            return page.render()
        json = {"json": json}
        print json
        page.add('json_viewer.tpl', json)
        return page.render()
