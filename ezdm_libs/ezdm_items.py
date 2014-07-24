from frontend import JSON_Editor
from item import Item


class ITEMS(JSON_Editor):
    def __init__(self):
        self._name = 'item'
        JSON_Editor.__init__(self)
        self._obj = Item({})
