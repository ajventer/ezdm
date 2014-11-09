from .util import debug
class MockCharacterList(object):
    def __init__(self):
        pass

    def index(self,key):
        return -1

class MockCampaign(object):
    def __init__(self):
        self.characterlist = MockCharacterList()

    def real(self):
        return False

    def message(self, *args):
        debug(*args)

    def warning(self,*args):
        self.message(*args)

    def error(self,*args):
        self.message(*args)