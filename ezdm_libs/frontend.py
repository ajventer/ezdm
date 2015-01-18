from jinja2 import Template
from .util import readfile, find_files, template_dict, json_editor, list_icons, inflate, load_json, user_hash, debug
from json import dumps, loads
from .mockclasses import MockCampaign

modevar = {}
campaign = MockCampaign()


def mode():
    global modevar
    myhash = user_hash()
    if myhash in modevar:
        return modevar[myhash]
    return 'campaign'


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
    def __init__(self, title=None, menu=True):
        self._sidebar = ''
        self._messages = {'messages': [], 'warnings': [], 'errors': []}
        self.title = title or 'EZDM'
        self.headerdict = {}
        if mode() == 'dm':
            menuitems = self.make_menu(find_files('', 'ezdm*.py', basename=True), 'ezdm_')
        else:
            menuitems = self.make_menu(find_files('', 'campaign*.py', basename=True), 'campaign_')
        menuitems.update(self.make_menu(find_files('', 'all*.py', basename=True), 'all_'))
        if mode() == 'dm':
            self.title += ' DUNGEON MASTER MODE'
        else:
            self.title += ' CAMPAIGN MODE'
        if campaign.real():
            self.headerdict['character'] = campaign.current_char()
            self.headerdict['characters'] = campaign.characterlist
        self._menuitems = {'menuitems': menuitems}
        self.content = [('menubar.tpl', self._menuitems)]

    def display_campaign_messages(self):
        if campaign.real():
            for message in campaign.messages:
                self._add_message(*message)
            campaign.messages = []

    def make_menu(self, files, base):
        out = {}
        for name in files:
            display = name.replace(base, '').replace('.py', '').upper()
            name = name.replace('.py', '').upper()
            out[name] = display
        return out

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
        self.display_campaign_messages()
        self.headerdict['title'] = self.title
        if self._has_message():
            self.headerdict['messages'] = self._messages
        self.content.insert(0, ('header.tpl', self.headerdict))
        if self._sidebar:
            self.content.insert(1, ('sidebar_top.tpl', {}))
            self.content.append(('sidebar.tpl', {'content': self._sidebar}))
        if not ('footer.tpl', {}) in self.content:
            self.content.append(('footer.tpl', {}))
        page_content = ''
        for item in self.content:
            page_content += self.tplrender(item[0], item[1])
        return page_content


class JSON_Editor(Session):

    _name = 'X'
    _sidebar = ''

    def __init__(self):
        self._obj = None
        Session.__init__(self)
        self._icons = 'icons'

    def _loadform(self, new=True):
        loadfrom = {}
        loadfrom['name'] = self._name
        loadfrom['keyname'] = 'loadfrom'
        if new:
            loadfrom['allow_new'] = True
        loadfrom['allow_raw'] = True
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

    def rawedit(self, default, page):
        if not default.endswith('.json'):
            default = '%s.json' % default
        json = load_json('%ss' % self._name, default)
        outdata = {'json': dumps(json, indent=4)}
        page.add('json_raw_editor.tpl', outdata)
        return page.render()

    def newform(self):
        page = Page()
        if self._icons:
            self.sidebar(page.tplrender('icon_selecter.tpl', list_icons(self._icons)))
        lf = self._loadform(False)
        page.add(lf[0], lf[1])
        default = self._data.get('loadfrom', None)
        if default and not default == 'New %s' % self._name:
            if 'raw_mode' in self._data:
                return self.rawedit(default, page)
            self._data = load_json('%ss' % self._name, '%s.json' % default)
        debug("Using template file: template_%s.json" % self._name)
        template = readfile('adnd2e', 'template_%s.json' % self._name, json=True)
        debug('data:')
        for key in sorted(self._data):
            debug('     ', key, self._data[key])
        tpldict = template_dict(template, self._data)
        debug("tpldict", tpldict)
        page.add('json_editor.tpl', json_editor(tpldict, 'New %s' % self._name, '/ezdm_%sS' % self._name.upper()))
        inflated = inflate(self._data)
        debug("inflated", inflated)
        if 'core' in inflated:
            duplicate_keys = [k for k in inflated if k in inflated['core']]
            for key in duplicate_keys:
                    del(self._data[key])
            debug("Data without dupes", self._data)
            if "save_changes" in self._data:
                debug("Saving changes")
                if 'save_changes' in inflated:
                    del(inflated['save_changes'])
                self._obj.update(inflated)
                page.message('%s saved to %s' % (self._name, self._obj.save()))
        if self._sidebar:
            page.sidebar(self._sidebar)
        return page.render()

    def render(self, requestdata):
        if mode() != 'dm':
            page = Page()
            page.error('Sorry, this feature cannot be used in campaign mode')
            return page.render()
        if not requestdata:
            return self.welcomeform()
        if 'saveraw' in requestdata:
            page = Page()
            try:
                json = loads(requestdata['json'])
                self._obj.update(json)
                page.message('%s saved to %s' % (self._name, self._obj.save()))
            except Exception as e:
                page.error("Invalid json: %s" % e)
            return self.rawedit(self._obj.name(), page)
        self._data = dict(requestdata)
        if 'LoadDefaultFrom' in self._data:
            del(self._data['LoadDefaultFrom'])
        return self.newform()

    def view(self, item):
        page = Page()
        page.message(item)
        if not item:
            page.error('No item specified')
            return page.render()
        try:
            debug('try %s' % self._name)
            json = readfile('%ss' % self._name, item, json=True)
        except:
            debug('except')
            page.error('No files matching %s found in %s' % (item, self._name))
            return page.render()
        json = {"json": json}
        page.add('json_viewer.tpl', json)
        return page.render()
