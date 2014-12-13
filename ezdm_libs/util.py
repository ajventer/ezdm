import os
from ezdm_libs import get_user_data, data_paths
from json import loads, dumps
from glob import glob
from random import randrange
import binascii
import sys
import bottle
import hashlib


def user_hash():
    user_string = '%s%s' % (bottle.request.environ.get('REMOTE_ADDR'), bottle.request.environ.get('HTTP_USER_AGENT'))
    user_string = user_string.encode('utf-8')
    return hashlib.sha224(user_string).hexdigest()



def debug(*args):
    out = '[DEBUG]:'
    for arg in args:
        out += ' ' + str(arg)
    sys.stderr.write('%s\n' % out)


def npc_hash():
    """
    >>> hashes = []
    >>> for i in range(1,1000):
    ...     hashes.append(npc_hash())
    ...
    >>> len(hashes) == len(list(set(hashes)))
    True
    """
    return str(binascii.b2a_hex(os.urandom(64)))


def json_editor(tpldict, name, action):
    return {'header': {'name': name, 'action': action}, 'formdata': tpldict}


def template_dict(template, defaults=None):
    tpl = flatten(template)
    dfl = defaults and flatten(defaults) or {}
    ret = {}
    for key in sorted(tpl):
        inputtype = 'text'
        options = []
        value = tpl[key]
        name = realkey(key)
        if key.startswith('conditional') and not defaults:
            continue
        if key.startswith('conditional'):
            condition = realkey(key.split('/')[1])
            name = key.split('/')
            del(name[1])
            name = realkey('/'.join(name))
            k, v = condition.split('=')
            k = k.replace('.', '/')
            dv = k in dfl and dfl[k]
            if dv == v:
                if name in dfl:
                    value = dfl[name]
                elif isinstance(tpl[key], str) and not tpl[key].startswith('__['):
                    value = tpl[key]
                elif isinstance(tpl[key], str) and tpl[key].startswith('__['):
                    options = tpl[key].replace('__[', '').replace(']', '').split(',')
                    inputtype = 'select'
                    value = ''
            else:
                continue

        if '__X' in key:
            continue
        if '__T' in key:
            inputtype = 'textarea'
        if '__Y' in key:
            inputtype = 'hidden'
        if isinstance(tpl[key], str) and tpl[key].startswith('__['):
            inputtype = 'select'
            options = tpl[key].replace('__[', '').replace(']', '').split(',')
        if realkey(key) in dfl:
            value = dfl[realkey(key)]
        elif realkey(key).replace('core/', '') in dfl:
            value = dfl[realkey(key).replace('core/', '')]
        if isinstance(value, str) and value.startswith('__['):
            value = ''
        ret[name] = {'name': name, 'value': value, 'inputtype': inputtype, 'options': options}
    if not 'conditional' in ret:
        ret['conditional'] = 'placeholder'
    return ret


def flatten(init, lkey=''):
    ret = {}
    for rkey, val in list(init.items()):
        key = lkey + rkey
        if isinstance(val, dict) and val:
            ret.update(flatten(val, key + '/'))
        else:
            ret[key] = val
    return ret


def inflate(dic):
    out = {}
    for key in dic:
        if isinstance(dic[key], str) and dic[key].lower() in ['true', 'false']:
            dic[key] = dic[key].lower()
        try:
            v = loads(dic[key])
        except:
            v = dic[key]
        writekey(key, v, out)
    return out


def save_json(source, name, dic):
    d = inflate(flatten(dic))
    if not name.endswith('.json'):
        name = '%s.json' % name
    filename = os.path.join(get_user_data(source), name).replace(' ', '_')
    handle = open(filename, 'w')
    handle.write(dumps(d, indent=4))
    handle.close()
    debug('Saving %s' % filename)
    return filename


def realkey(key):
    ret = []
    for k in key.split('/'):
        if k.startswith('__'):
            ret.append(k[3:])
        else:
            ret.append(k)
    return '/'.join(ret).strip('/')

def indexkey(k):
    if len(k) >= 2 and k.startswith('i') and k[1].isdigit():
        return int(k[1:])
    return '"%s"' % k


def readkey(key, json, default=None):
    """
    >>> readkey('/x', {'x':1})
    1
    >>> readkey('/x/y', {'x': {'y': 1}})
    1
    >>> readkey('/x/i1', {'x': [1,2,3]})
    2
    >>> readkey('/x/i10', {'x': [0,1,2,3,4,5,6,7,8,9,10,11]})
    10
    """
    if not isinstance(json, dict):
        raise ValueError("%s must be a dict" % repr(json))
    key = key.strip('/')
    keylist = key.split('/')
    keystring = 'json'
    for k in keylist:
        k = indexkey(k)
        keystring = '%s[%s]' % (keystring, k)
    try:
        return eval(keystring)
    except:
        return default

def writekey(key, value, json):
    """
    >>> x = {'y':1, 'z':[{'a':1},{'b':2}]}
    >>> writekey('/y', 2, x)
    >>> x['y']
    2
    >>> writekey('/z/i0/a', 2, x)
    >>> x['z'][0]['a']
    2
    """
    parse = 'json'
    for k in key.strip('/').split('/'):
        k = k.replace('/', '')
        k = indexkey(k)
        new_parse = '%s[%s]' % (parse, k)
        exec ('if %s is not None and not %s in %s: %s = {}' % (parse, k, parse, new_parse))
        parse = new_parse
    parse = '%s = value' % (parse)
    exec (parse)


def list_icons(source='icons'):
    icons = find_files(source, '*')
    icons = [os.path.join(source, os.path.basename(icon)) for icon in icons]
    return {'icons': icons}


def load_icon(icon='icons/blank.png'):
    if '/' in icon:
        source, icon = icon.split('/')
    else:
        source = 'icons'
    path = ''
    for p in data_paths(source):
        if os.path.exists(os.path.join(p, icon)):
            path = os.path.join(p, icon)
    if path == '':
        path = os.path.join(data_paths('icons')[0], 'blank.png')
    return path


def find_files(source, needle='', basename=False, strip=''):
    debug('Searching for %s in %s' % (needle, source))
    matches = []
    for path in data_paths(source):
        debug('Checking path %s' % path)
        if path:
            matches += glob(os.path.join(path, '%s*' % needle))
    if basename:
        matches = [os.path.basename(match) for match in matches]
    if strip:
        matches = [match.replace(strip, '') for match in matches]
    debug('Found matches:', matches)
    unique = {}
    for m in matches:
        bname = os.path.basename(m)
        if not bname in unique:
            unique[bname] = m
    result = []
    for k,v in list(unique.items()):
        result.append(v)
    return result


def readfile(source='', name='', filename='', json=False, default=None):
    debug('%s - %s: %s' % (source, name, filename))
    if not filename:
        filenames = find_files(source, name)
        if filenames:
            filename = filenames[0]
    handle=open(filename, 'r')
    s = handle.read()
    debug(s)
    handle.close()
    if not json:
        try:
            return s
        except:
            return default
    try:
        debug('Attempting json load')
        return loads(s)
    except Exception as E:
        debug(E)
        return default


def load_json(source='', name='', filename='', default=None):
    if name and not name.endswith('.json'):
        name = '%s.json' % name
    return readfile(source=source, name=name, filename=filename, json=True, default=default)


def attack_mods():
    handle = open(os.path.join(get_user_data('adnd2e'), "attack_mods.json"))
    s = handle.read()
    handle.close()
    return loads(s)


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
    """
    >>> inrange(5,'6-7')
    False
    >>> inrange(5,'5')
    True
    >>> inrange(5,'4-7')
    True
    """
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


def rolldice(numdice=1, numsides=20, modifier=0):
    """
    >>> x = rolldice(numdice=5, numsides=20, modifier=0)
    >>> x[0] >= 1
    True
    >>> x[0] <= 100
    True
    """
    total = 0
    numdice = int(numdice)
    numsides = int(numsides)
    modifier = int(modifier)
    for I in range(0, numdice):
            if numsides == 1:
                roll = randrange(0, numsides, 1)
            else:
                roll = randrange(1, numsides, 1)
            total = total + roll + modifier
    return (total, 'Rolled a %s-sided dice %s times with modifier %s: result %s' % (numsides, numdice, modifier, total))
