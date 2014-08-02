from util import readkey, writekey
from simplejson import dumps


def event(obj, key, localvars):
    code = obj.get(key, '')
    if code:
        exec code in {}, localvars


class EzdmObject(object):
    json = {}

    def __init__(self, json):
        self.json = json

    def __call__(self):
        return self.json

    def __str__(self):
        return dumps(self(), indent=4)

    def update(self, json):
        self.__init__(json)

    def get(self, key, default):
        if not self():
            return default
        return readkey(key, self(), default)

    def put(self, key, value):
        return writekey(key, value, self.json)

    def save(self):
        pass
