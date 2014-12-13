import os
from .util import readkey, writekey, debug
from json import dumps
from .frontend import mode, datastore


def event(obj, key, localvars):
    code = obj.get(key, '')
    debug('Got code %s' % code)
    #localvars['campaign'] = campaign()
    if code:
        try:
            exec (code, {}, localvars)
        except Exception as e:
            raise Exception("Exception %s, while running event code, key: %s, object: %s, localvars: %s\n%s" % (e, key, obj.displayname(), localvars, code))


class EzdmObject(object):
    json = {}

    def __init__(self, key):
        if key.endswith('.json'):
            key = key.replace('.json', '')
        self.key = key
        datastore.readkey(self.key, {})
        

    def __call__(self):
        """
        >>> o = EzdmObject('characters/bardic_rogue')
        >>> o()['core']['type'] == 'player'
        True
        """
        return datastore.readkey(self.key)

    def __str__(self):
        return dumps(self(), indent=4, sort_keys=True).strip()


    def get(self, key, default=None):
        """
        >>> o = EzdmObject('characters/bardic_rogue')
        >>> o.get('/core/type', '') == 'player'
        True
        >>> o.get('/f/g', 5)
        5
        """
        if not self():
            return default
        return readkey(key, self(), default)


    def put(self, key, value):
        """
        >>> o = EzdmObject('characters/bardic_rogue')
        >>> o.put('f/g', 16)
        >>> o()['f']['g']
        16
        """
        while key.startswith('/'):
            key = key[1:]
        key = os.path.join(self.key, key)
        datastore.writekey(key, value)

    def save(self):
        datastore.save()
