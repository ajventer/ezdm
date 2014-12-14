import json
from .util import load_json, save_json, debug, find_files
from .util import readkey as json_readkey
from .util import writekey as json_writekey
from multiprocessing import Pool


def save_worker(data):
    dirname, filename, dic = data
    return save_json(dirname, filename, dic)


class Datastore(dict):
    """
    An extended dictionary for holding a consistent datastore
    """
    def readkey(self, key, default=None):
        """
        >>> x = Datastore()
        >>> x.readkey('characters/bardic_rogue/core/type')
        'player'
        """
        key = key.replace('//', '/').strip('/')
        keylist = key.split('/')
        if len(keylist) >= 2:
            directory, filename = keylist[:2]
            if not directory in self:
                self[directory] = {}
            if filename.endswith('.json'):
                filename = filename.replace('.json','')
            if not filename in self[directory]:
                paths = find_files(directory, filename)
                if paths:
                    self[directory][filename] = load_json(filename=paths[0])
        return json_readkey(key, self, default)



    def writekey(self, key, value):
        """
        >>> x = Datastore()
        >>> x.writekey('/x/y', 9)
        >>> x.readkey('/x/y')
        9
        """
        keylist = key.split('/')
        if len(keylist) >= 2:
            if keylist[1].endswith('.json'):
                keylist[1].replace('.json','')
                key = '/'.join(keylist)
        json_writekey(key, value, self)


    def save(self):
        """
        >>> x = Datastore()
        >>> x.readkey('characters/bardic_rogue/core/type')
        'player'
        >>> x.save()
        [...]
        """
        return
        workload = []
        pool = Pool()
        for directory in self.keys():
            for filename in self[directory].keys():
                workload.append((directory, filename, self[directory][filename]))
        return pool.map(save_worker, workload)




