from util import inflate, flatten, rolldice, readfile, inrange, price_in_copper, convert_money, save_json, load_json, readkey
from item import Item
from objects import EzdmObject, event


class Character(EzdmObject):
    removed = False
    cast_remaining = 0
    spell_target = None
    json = {}
    auto = False
    index = -1
    weapon = 0
    weapons = []
    armor = []

    def __init__(self, json):
        print "Instantiating character"
        self.json = json
        try:
            self.weapons = self.load_weapons()
            self.armor = self.load_armor()
            self.put('core/combat/thac0', self.__get_thac0())
            self.put('core/combat/saving_throws', self.__get_saving_throws())
            if self.is_monster():
                self.put('core/combat/hitpoints', rolldice(numdice=int(self.get('/combat/level-hitdice', '1')), numsides=8))
                self.put('core/combat/max_hp', self.get('/combat/hitpoints', 1))
        except:
            pass

    def oninteract(self, target, page):
        event(self, '/conditional/events/oninteract', {'character': self, 'page': page, 'target': target})

    def remove_from_combat(self):
        self.removed = True

    def xp_worth(self):
        xpkey = self.get('core/combat/level-hitdice', 1)
        xpvalues = readfile('adnd2e', 'creature_xp', json=True, default={})
        if str(xpkey) in xpvalues.keys():
            xp = xpvalues[str(xpkey)]
        elif int(xpkey) > 12:
            xp = 3000 + ((int(xpkey) - 13) * 1000)
        return int(xp)

    def set_index(self, index):
        self.index = index

    def heal(self, amount):
        hp = int(self.get('/core/combat/hitpoints', 1))
        hp += amount
        if hp > int(self.get('/core/combat/max_hp', 1)):
            self.put('/core/combat/hitpoints', int(self.get('/core/combat/max_hp', 1)))
        else:
            self.put('/core/combat/hitpoints', hp)
            return self.get('/core/combat/hitpoints')

    def take_damage(self, damage):
        out = []
        if damage >= self.get('/core/combat/hitpoints', 1):
            st = self.saving_throw('ppd')
            out = st[1]
            if not st[0]:
                self.put('/core/combat/hitpoints', 0)
                out += "%s has died !" % self.displayname()
                return (False, out)
            else:
                self.put('/core/combat/hitpoints', 1)
                out += "%s barely survives. %s hitpoints remaining" % (self.displayname(), self.get('/core/combat/hitpoints', 1))
                return (True, out)
        else:
            hp = int(self.get('/core/combat/hitpoins', 1))
            hp -= damage
            self.put('/core/combat/hitpoins', hp)
            out += "%s takes %s damage. %s hitpoints remaining" % (self.displayname(), damage, self.get('/core/combat/hitpoints', 1))
            return (True, out)

    def is_monster(self):
        return self.get('/core/personal/race', '') in ['creature', 'monster']

    def start_casting(self, rounds, target):
        self.cast_remaining = rounds
        self.spell_target = target

    def continue_casting(self):
        self.cast_remaining -= 1
        return self.is_casting()

    def is_casting(self):
        return self.cast_remaining > 0

    def interrupt_cast(self, by=''):
        self.spell_complete()
        return '%s: spell casting interrupted %s !' % (self.displayname(), by)

    def spell_complete(self):
        self.cast_remaining = 0
        self.spell_target = None

    def spell_friendly_target(self):
        return self.is_monster() == self.spell_target.is_monster()

    def save(self):
        self.json = inflate(flatten(self.json))
        if 'temp' in self():
            del self()['temp']
        name = '%s_%s.json' % (self.get('/core/personal/name/first', ''), self.get('/core/personal/name/last', ''))
        return save_json('characters', name.lower(), self.json)

    def to_hit_mod(self):
        ability_mods = readfile('adnd2e', 'ability_scores', json=True)
        base = int(ability_mods["str"][str(self()['abilities']['str'])]['hit'])
        if len(self.weapons) > 0:
            bonus = int(readkey('/conditionals/tohit', self.weapons[self.weapon].json, 0))
        else:
            bonus = 0
        return base + bonus

    def ppd_mod(self):
        ability_mods = readfile('adnd2e', 'ability_scores', json=True)
        return int(ability_mods["con"][str(self()['abilities']['con'])]['ppd'])

    def dmg_mod(self):
        ability_mods = readfile('adnd2e', 'ability_scores', json=True)
        return int(readkey('/str/%s/dmg' % self.get('/abilities/str', 0), ability_mods, 0))

    def def_mod(self):
        ability_mods = readfile('adnd2e', 'ability_scores', json=True)
        return int(readkey('/dex/%s/defense' % self.get('/abilities/dex', 0), ability_mods, 0))

    def __get_saving_throws(self):
        key = self.get('/core/class/parent', '')
        sts = load_json("adnd2e", "saving_throws")[key]
        hitdice = self.get('/core/combat/level-hitdice', 0)
        for key2 in sts.keys():
            if inrange(hitdice, key2):
                st = sts[key2]
                st['ppd'] = int(st['ppd']) + self.ppd_mod()
                return(st)

    def saving_throw(self, against):
        saving = load_json('adnd2e', 'saving_throws') or {}
        prettyname = saving['names'][against]
        race = self.get('/core/personal/race', '')
        con = int(self.get('/core/abilities/con', 0))
        mod = 0
        if race in saving.keys():
            for key in saving[race].keys():
                if inrange(con, key):
                    mod = int(saving[race][key])
                    continue
        target = int(self.get('/core/combat/saving_throws/%s' % against, 0))
        out = ["%s Tries to roll a saving throw against %s" % (self.displayname(), prettyname), "%s needs to roll %s" % (self.displayname(), target)]
        roll = rolldice(numdice=1, numsides=20, modifier=mod)
        out.append(roll[1])
        if roll[0] >= int(target):
            out.append('Saved !')
            return (True, out)
        else:
            out.append("Did not save !")
            return (False, out)

    def dmg(self, weapon):
        return int(readkey('/conditionals/dmg', self.weapons[weapon](), 0))

    def hit_dice(self):
        if self.is_monster():
            return int(self.get('/core/combat/level-hitdice', 1))
        else:
            return 1

    def autoroll(self):
        return self.auto

    def current_weapon(self):
        return self.weapon

    def reset_weapon(self):
        self.weapon = 0

    def next_weapon(self):
        self.weapon += 1
        if self.weapon > self.num_weapons() - 1:
            self.weapon = 0

    def give_xp(self, xp):
        current_xp = int(self.get('/core/personal/xp', 0))
        new_xp = current_xp + int(xp)
        self.put('/core/personal/xp', str(new_xp))
        return str(new_xp)

    def next_level(self):
        parentclass = self.get('/core/class/parent', '')
        childclass = self.get('/core/class/class', '')
        nl = int(self.get('/combat/level-hitdice', '')) + 1
        xp_levels = readkey('/%s/%s' % (parentclass, str(nl)), load_json('adnd2e', 'xp_levels'), {})
        if 'all' in xp_levels:
            next_xp = int(xp_levels['all'])
        else:
            next_xp = int(xp_levels[childclass])
        return next_xp

    def is_misile(self):
        try:
            return self.weapons[self.weapon]['conditionals']['weapon_type'] == "misile"
        except IndexError:
            return False

    def attack_roll(self, target, mod):
        self.next_weapon()
        roll = rolldice(numdice=1, numsides=20, modifier=mod)
        if roll[0] - mod == 1:
                return ("Critical Miss !", roll[1])
        elif roll[0] - mod == 20:
            return ("Critical Hit !", roll[1])
        else:
            if roll[0] >= self.__get_thac0() - target.armor_class() - target.def_mod():
                return ("Hit !", roll[1])
            else:
                return ("Miss !", roll[1])

    def spell_success(self):
        ability_scores = load_json('adnd2e', 'ability_scores')
        wis = str(self.get('/core/abilities/wis', 0))
        failrate = int(ability_scores["wis"][wis]["spell_failure"].split('%')[0])
        out = ["Spell failure rate: %s percent" % failrate]
        roll = rolldice(numdice=1, numsides=100)
        out.append(roll[1])
        if roll[0] > failrate:
            out.append('Spell succeeds !')
            return (True, out)
        else:
            out.append('Spell fails !')
            self.spell_complete()
            return(False, out)

    def load_weapons(self):
        weap = []
        if not "inventory" in self() or not "equiped" in self()["inventory"]:
            return []
        for slot in ['righthand', 'lefthand']:
            item = Item(self.get('/core/inventory/equiped/%s' % slot, {}))
            if item and not item.slot == 'twohand' and slot == 'lefthand':
                weap.append(item)
            elif item.slot == 'twohand' and not item.slot == 'righthand':
                weap = [item]
        return weap

    def acquire_item(self, item):
        self()['core']['inventory']['pack'].append(item())

    def equip_item(self, itemname):
        slots = []
        has_unequiped = False
        for item in [Item(i) for i in self.get('/core/inventory/pack', [])]:
            if item.displayname == itemname:
                break
        if item:
            if item.slot() == 'twohand':
                slots = ['lefthand', 'righthand']
            elif item.slot() == 'finger':
                left = self.get('/core/inventory/leftfinger', {})
                right = self.get('/core/inventory/rightfinger', {})
                #Hint for best results - drop a ring before equiping another
                if not left:
                    slots = ['leftfinger']
                if not right:
                    slots = ['rightfinger']
                if not slots:
                    slots = ['leftfinger']
            else:
                slots = [item.slot()]
            for slot in slots:
                if self.get('/core/inventory/equipped/%s' % item.slot(), {}) and not has_unequiped:
                    self.unequip(slot)
                    #Prevent equipping over a twohander from duplicatng it
                    has_unequiped = True
                self.put('/core/inventory/equiped/%s' % slot, item())
                self.drop_item(item.displayname())

    def unequip_item(self, slot):
        current = self.get('/core/inventory/equiped/%s' % slot, {})
        if current:
            self.json['inventory']['pack'].append(current)
        self.put('/core/inventory/equiped/%s' % slot, {})

    def sell_item(self, itemname, buyer='shop', gold=0, silver=0, copper=0):
        for item in self.get('/inventory/pack'):
            if item.displayname() == itemname:
                tosell = Item(item)
                break
        if buyer != 'shop':
            buyer.spend_money(gold, silver, copper)
            buyer.acquire_item(tosell())
        else:
            gold, silver, copper = item.money_tuple().items()
        self.drop_item(itemname)
        self.gain_money(gold, silver, copper)

    def drop_item(self, itemname, section='pack'):
        for item in self.get('/core/inventory/%s' % section, []):
            item = Item(item)
            if item.displayname() == itemname:

                i = self.get('/core/inventory/%s' % section, []).index(item())
                del self.json['core']['inventory'][section][i]

    def list_inventory(self, sections=['pack', 'equiped']):
        result = []
        for section in sections:
                result.extend(self.get('/core/inventory/%s' % section, []))
        return result

    def money_tuple(self):
        gold = self.get('/core/inventory/money/gold', 0)
        silver = self.get('/core/inventory/money/silver', 0)
        copper = self.get('/core/inventory/money/copper', 0)
        return (int(gold), int(silver), int(copper))

    def spend_money(self, gold=0, silver=0, copper=0):
        ihave = price_in_copper(*self.money_tuple())
        price = price_in_copper(gold, silver, copper)
        remains = ihave - price
        if remains < 0:
            return False
        else:
            self.put('/core/inventory/money', convert_money(remains))
            return True

    def buy_item(self, item):
        price = readkey('/price', item(), {"gold": 0, "silver": 0, "copper": 0})
        if self.spend_money(int(price['gold']), int(price['silver']), int(price['copper'])):
            self.acquire_item(item)
            return True
        else:
            return False

    def gain_money(self, gold=0, silver=0, copper=0):
        total_gained = price_in_copper(gold, silver, copper)
        my_total = price_in_copper(*self.money_tuple())
        my_total += total_gained
        self.put('/core/inventory/money', convert_money(my_total))

    def armor_class(self):
        AC = 10
        for item in self.armor:
            AC -= int(readkey('/conditionals/ac', item()), 0)
        return AC

    def load_armor(self):
        arm = []
        if not "inventory" in self() or not "equiped" in self()["inventory"]:
            return []
        for item in self.list_inventory(['equiped']):
            if item['type'] == 'armor':
                arm.append(Item(item))
        return arm

    def num_weapons(self):
        return len(self.weapons)

    def num_attacks(self):
        atr = readkey('/various/attacks_per_round', readfile('adnd2e', 'various', json=True), 0)
        parentclass = self.get('/class/parent', '')
        if not parentclass in atr:
            ATR = 1
        else:
            for key in atr[parentclass].keys():
                if inrange(self.get('/core/combat/level-hitdice', 1), key):
                    ATR = int(atr[parentclass][key])
        return self.num_weapons() * int(ATR)

    def current_xp(self):
        return int(self.get('/core/personal/xp', 0))

    def tryability(self, ability, modifier=0):
        out = ['%s is trying to %s' % (self.displayname(), ability)]
        target_roll = int(self.conditionals()[ability])
        target_roll += int(modifier)
        out.append('%s must roll %s or lower to succeed' % (self.displayname(), target_roll))
        roll = rolldice(numdice=1, numsides=100)
        out.append(roll[1])
        if roll[0] <= target_roll:
            return (True, out)
        else:
            return (False, out)

    def conditionals(self):
        subclass = self.get('/core/class/class', '')
        parentclass = self.get('/core/class/parent', '')
        level = self.get('/core/combat/level-hitdice', '')
        various = load_json('adnd2e', 'various')
        abilities = various['abilities']
        conditionals = self.get('/conditionals', {})
        race = self.get('/core/personal/race', self())
        for ability in abilities:
            base = 0
            if ability in conditionals:
                if isinstance(conditionals[ability], str) and len(conditionals[ability]) > 0:
                    base = int(conditionals[ability])
            if subclass in abilities[ability]:
                for key in abilities[ability][subclass]:
                    if inrange(level, key):
                        base += int(abilities[ability][subclass][key])
                        continue
            elif parentclass in abilities[ability]:
                for key in abilities[ability][parentclass]:
                    if inrange(level, key):
                        base += int(abilities[ability][parentclass][key])
                        continue
            if base > 0:
                if race in abilities[ability]:
                    base += int(abilities[ability][race])
                conditionals[ability] = base
        for key in conditionals:
            racial_bonus = 0
            if "racial_bonus" in various['abilities'][key] and race in various['abilities'][key]["racial_bonus"]:
                racial_bonus = int(various['abilities'][key]["racial_bonus"][race])
            dex = int(self.get('/abilities/dex', 0))
            dex_bonus = 0
            if "dexterity bonus" in various['abilities'][key]:
                for d in various['abilities'][key]["dexterity bonus"]:
                    if inrange(dex, d):
                        dex_bonus = int(various['abilities'][key]["dexterity bonus"][d])
                        continue
            if isinstance(conditionals[key], str) and len(conditionals[key]) == 0:
                conditionals[key] = 0
            if int(conditionals[key]) > 0:
                conditionals[key] = int(conditionals[key]) + dex_bonus + racial_bonus
        return conditionals

    def displayname(self):
        out = "%s %s" % (self.get('/core/personal/name/first', ''), self.get('/core/personal/name/last', ''))
        if self.index > -1:
            out = "%s (%s)" % (out, self.index)
        out = "[%s]" % out
        return out

    def __get_thac0(self):
        if self.get('/core/personal/race', '') == "creature":
            key = "creature"
        else:
            key = self.get('/core/class/parent', '')
        thac0s = load_json("adnd2e", "thac0")[key]
        for key2 in thac0s.keys():
            if inrange(self.get('/core/combat/level-hitdice', 1), key2):
                return int(thac0s[key2])
