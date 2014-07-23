import os
from ezdm_libs import get_sys_data, get_user_data
from simplejson import loads, dumps
from glob import glob
from random import randrange


def json_editor(tpldict, name, action):
    return {'header': {'name': name, 'action': action}, 'formdata': tpldict}


def template_dict(template, defaults=None):
    tpl = flatten(template)
    dfl = defaults and flatten(defaults) or {}
    ret = {}
    for key in tpl:
        inputtype = 'text'
        options = []
        value = ''
        name = realkey(key)
        if key.startswith('conditional') and not defaults:
            continue
        if key.startswith('conditional'):
            condition = key.split('/')[1]
            name = key.split('/')
            del(name[1])
            name = realkey('/'.join(name))
            k, v = condition.split('=')
            k = k.replace('.', '/')
            dv = k in dfl and dfl[k]
            if dv == v:
                if name in dfl:
                    value = dfl[name]
                elif not tpl[key].startswith('__['):
                    value = tpl[key]
                else:
                    options = tpl[key].replace('__[', '').replace(']', '').split(',')
                    inputtype = 'select'
            else:
                continue
        if '__' in key:
            for k in key.split('/'):
                if k.startswith('__X'):
                    break
                if k.startswith('__Y'):
                    inputtype = 'hidden'
        if isinstance(tpl[key], str) and tpl[key].startswith('__['):
            inputtype = 'select'
            options = tpl[key].replace('__[', '').replace(']', '').split(',')
        if realkey(key) in dfl:
            value = dfl[realkey(key)]
        elif realkey(key).replace('core/', '') in dfl:
            value = dfl[realkey(key).replace('core/', '')]
        ret[name] = {'name': name, 'value': value, 'inputtype': inputtype, 'options': options}
    return ret


def flatten(init, lkey=''):
    ret = {}
    for rkey, val in init.items():
        key = lkey + rkey
        if isinstance(val, dict):
            ret.update(flatten(val, key + '/'))
        else:
            ret[key] = val
    return ret


def save_json(source, name, dic):
    d = flatten(dic)
    out = {}
    if not name.endswith('.json'):
        name = '%s.json' % name
    filename = os.path.join(get_user_data(source), name)
    for key in d:
        writekey(key, d[key], out)
    open(filename, 'w').write(dumps(out, indent=4))
    return filename


def realkey(key):
    ret = []
    for k in key.split('/'):
        if k.startswith('__'):
            ret.append(k[3:])
        else:
            ret.append(k)
    return '/'.join(ret).strip('/')


def readkey(key, json, default=None):
    if not json or not isinstance(json, dict):
        raise ValueError("%s must be a dict" % repr(json))
    key = key.strip('/')
    keylist = key.split('/')
    for k in keylist:
        k = k.replace('/', '')
        if not k in json:
            return default
        if keylist.index(k) == len(keylist) - 1:
            return json[k]
        else:
            ks = '/'.join(keylist[keylist.index(k) + 1:])
            return readkey(ks, json[k], default)


def writekey(key, value, json):
    parse = 'json'
    for k in key.strip('/').split('/'):
        k = k.replace('/', '')
        new_parse = '%s["%s"]' % (parse, k)
        exec 'if not "%s" in %s: %s = {}' % (k, parse, new_parse)
        parse = new_parse
    parse = '%s = value' % (parse)
    exec parse


def load_icon(icon='blank.png'):
    syspath = get_sys_data('icons')
    userpath = get_user_data('icons')
    path = ''
    if os.path.exists(os.path.join(syspath, icon)):
        path = os.path.join(syspath, icon)
    if os.path.exists(os.path.join(userpath, icon)):
        path = os.path.join(userpath, icon)
    if path == '':
        path = os.path.join(syspath, 'blank.png')
    return path


def find_files(source, needle=None, basename=False, strip=''):
    matches = glob(os.path.join(get_user_data(source), needle))
    matches += glob(os.path.join(get_sys_data(source), needle))
    if basename:
        matches = [os.path.basename(match) for match in matches]
    if strip:
        matches = [match.replace(strip, '') for match in matches]
    return list(set(matches))


def readfile(source, name, json=False):
    filenames = find_files(source, name)
    if filenames:
        filename = filenames[0]
    if not json:
        return open(filename, 'r').read()
    return loads(open(filename, 'r').read())


def attack_mods():
    return loads(open(os.path.join(get_user_data('adnd2e'), "attack_mods.json")).read())


def price_in_copper(gold, silver, copper):
    s = gold * 10 + silver
    c = s * 10 + copper
    return c


def convert_money(copper):
    money = {"gold": 0, "silver": 0, "copper": copper}
    while money['copper'] > 10:
        money['silver'] += 1
        money['copper'] -= 10
    while money['silver'] > 10:
        money['gold'] += 1
        money['silver'] -= 10
    return money


def dice_list():
    return ['4', '6', '8', '10', '100', '12', '20']


def inrange(key1, key2):
        if '-' in key2:
            minimum = int(key2.split('-')[0])
            maximum = int(key2.split('-')[1])
        else:
            minimum = int(key2)
            maximum = minimum
        if int(key1) >= minimum and int(key1) <= maximum:
            return True
        else:
            return False


def rolldice(auto=True, numdice=1, numsides=20, modifier=0, quiet=False, wsgi=False):
    total = 0
    for I in range(1, numdice + 1):
            roll = randrange(1, numsides, 1)
            total = total + roll
    return total
