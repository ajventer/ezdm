from frontend import JSON_Editor
from campaign import Campaign


class CAMPAIGNS(JSON_Editor):
    def __init__(self):
        self._name = 'campaign'
        JSON_Editor.__init__(self)
        self._obj = Campaign({})
