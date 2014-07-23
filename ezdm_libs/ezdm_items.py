from frontend import JSON_Editor


class ITEMS(JSON_Editor):
    def __init__(self):
        self._name = 'item'
        JSON_Editor.__init__(self)
