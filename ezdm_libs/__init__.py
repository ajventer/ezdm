import os
from simplejson import loads


def data_paths(path):
    paths = []
    for source in [get_user_data, get_settings_data, get_sys_data]:
        data = source(path)
        if data:
            paths.append(data)
    return paths


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


def get_settings_data(path):
    for p in get_user_data('settingss') or [] + get_sys_data('settingss') or []:
        filename = os.path.join(p, 'settings.json')
        if os.path.exists(filename):
            break
        else:
            filename = None
    if not filename:
        return None
    try:
        json = loads(open(filename, 'r').read())
        p = json['core']['extra_data_paths']
        for pth in p:
            pt = os.path.join(pth, path)
            if os.path.exists(pt):
                return pt
    finally:
        return None
