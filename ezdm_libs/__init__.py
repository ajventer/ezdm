import os


def data_paths(path):
    return [get_sys_data(path), get_user_data(path)]


def get_user_data(path):
    _ROOT = os.path.expanduser('~')
    _ROOT = os.path.join(_ROOT, '.ezdm')
    datapath = os.path.join(_ROOT, path)
    if not os.path.exists(datapath):
        os.makedirs(datapath)
    return datapath


def get_sys_data(path):
    datapath = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
    if os.path.exists(datapath):
        return datapath
    else:
        return None
