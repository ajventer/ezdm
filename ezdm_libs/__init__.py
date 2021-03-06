import os
import sys


def data_paths(path):
    paths = []
    for source in [get_user_data, get_settings_data, get_sys_data]:
        data = source(path)
        if data:
            if isinstance(data, str):
                paths.append(data)
            else:
                paths.extend(data)
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
    paths = []
    if os.path.exists('/etc/ezdm/settings.py'):
        sys.path.append('/etc/ezdm')
        import settings
        for pth in settings.extrapaths:
            if os.path.exists(os.path.join(pth, path)):
                paths.append(os.path.join(pth, path))
    return paths
