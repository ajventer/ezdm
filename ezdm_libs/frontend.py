from jinja2 import Template
from util import readfile, find_files

class json_input:
    def __init__(self, template, defaults=None):
        self._template = template
        self._defaults = defaults or {}
        self._data = self._parsetemplate(self._template, self._defaults)

    def _realkey(self, keyname):
        if keyname.startswith('__'):
            return keyname[3:]
        else:
            return keyname

    def parsetemplate(self, template, defaults):
        data = {}
        for key in template:
            if isinstance(key, dict):
                data[realkey(key)] = self.parsetemplate(template.get(key), defaults.get(key))


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


class Page:
    def __init__(self, title=None):
        title = title or 'EZDM'
        menuitems = find_files('', 'ezdm*.py', basename=True)
        menuitems = [m.replace('ezdm_', '').replace('.py', '').upper() for m in menuitems]
        self._menuitems = {'menuitems': menuitems}

        self.content = [('header.tpl', {'title': title}), ('menubar.tpl', self._menuitems)]

    def _tplrender(self, name, data):
        tpl = Template(readfile('templates', name))
        return tpl.render(data)

    def add(self, template, data):
        self.content.append((template, data))

    def render(self):
        if not ('footer.tpl', {}) in self.content:
            self.content.append(('menubar.tpl', self._menuitems))
            self.content.append(('footer.tpl', {}))
        page_content = ''
        for item in self.content:
            page_content += self._tplrender(item[0], item[1])
        return page_content
