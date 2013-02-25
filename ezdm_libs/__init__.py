import os

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_sys_data(path):
    datapath=os.path.join(_ROOT,path)
    if os.path.exists(datapath):
        return  datapath
    else:
        return None

