from frontend import JSON_Editor
import frontend
from character import Character
from frontend import Page
from util import load_json


class CHARACTERS(JSON_Editor):
    def __init__(self):
        self._name = 'character'
        JSON_Editor.__init__(self)
        self._icons = 'avatars'
        self._obj = Character({})

    def render(self, requestdata):
        if frontend.mode == 'dm':
            return JSON_Editor.render(self, requestdata)
        else:
            char = frontend.campaign.current_char()
            return self.view(char.name())

    def view(self, item):
        page = Page()
        if not item:
            page.error('No item specified')
            return page.render()
        try:
            print 'try %s/%s' % (self._name, item)
            json = load_json('%ss' % self._name, item)
        except:
            print 'except'
            page.error('No files matching %s found in %s' % (item, self._name))
            return page.render()
        c = Character(json)
        rendered = {}
        rendered['json'] = c.render()
        return page.tplrender('json_viewer.tpl', rendered)
