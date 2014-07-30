from util import inflate, flatten, rolldice, readfile, inrange, price_in_copper, convert_money, save_json, load_json, readkey
from item import Item
from objects import EzdmObject, event
from gamemap import GameMap


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
            if not self.character_type() == 'player':
                self.put('core/combat/hitpoints', rolldice(numdice=int(self.get('/combat/level-hitdice', '1')), numsides=8))
                self.put('core/combat/max_hp', self.get('/combat/hitpoints', 1))
        except:
            pass

    def location(self):
        return self.get('/core/location', {})

    def moveto(self, mapname, x, y):
        current = self.location()
        if current.get('map'):
            gamemap = GameMap(load_json('maps', current['map']))
            gamemap.removefromtile(current['x'], current['y'], self.name(), 'players')
            print "Saving", gamemap.save()
        self.put('/core/location/x', x)
        self.put('/core/location/y', y)
        self.put('/core/location/map', mapname)
        gamemap = GameMap(load_json('maps', mapname))
        gamemap.addtotile(x, y, self.name(), 'players')
        print "Saving", gamemap.save()

    def character_type(self):
        return self.get('/core/type', 'player')

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

    def name(self):
        name = '%s_%s.json' % (self.get('/core/personal/name/first', ''), self.get('/core/personal/name/last', ''))
        return name.lower()

    def save(self):
        self.json = inflate(flatten(self.json))
        if 'temp' in self():
            del self()['temp']
        return save_json('characters', self.name(), self.json)

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

    def level_up(self):
        level = int(self.get('/core/combat/level-hitdice', 1))
        level += 1
        out = '%s has reached level %s !' % (self.displayname(), level)
        self.put('/core/combat/level-hitdice', level)
        ability_scores = load_json('adnd2e', 'ability_scores')
        con = self.get('/core/abilities/con', 1)
        out += '<br>Character constitution: %s' % con
        con_bonus = int(readkey('/con/%s/hit' % con, ability_scores, 0))
        out += '<br>Constitution Bonus: %s' % con_bonus
        xp_levels = load_json('adnd2e', 'xp_levels')
        pclass = self.get('/core/class/parent', '')
        xp_levels = readkey('%s' % (pclass), xp_levels)
        hitdice = readkey('/%s/hit_dice' % (level), xp_levels, 1)
        print "Read hitdice as ", hitdice
        if not '+' in hitdice:
            hitdice = hitdice + '+0'
        hitdice, bonus = hitdice.split('+')
        dice = int(readkey('/dice', xp_levels, 1))
        more_hp, roll = rolldice(numdice=int(hitdice), numsides=dice, modifier=con_bonus)
        out += '<br>%s' % roll
        more_hp += int(bonus)
        current_max = int(self.get('/core/combat/max_hp', 1))
        new_max = current_max + more_hp
        out += '<br>Maximum hitpoints increased by %s. Maximum hitpoints now: %s' % (more_hp, new_max)
        self.put('core/combat/max_hp', new_max)
        current_hp = int(self.get('/core/combat/hitpoints', 0))
        new_hp = current_hp + more_hp
        out += '<br>Character hitpoints now %s' % new_hp
        self.put('/core/combat/hitpoints', new_hp)
        return out

    def give_xp(self, xp, page):
        current_xp = int(self.get('/core/personal/xp', 0))
        new_xp = current_xp + int(xp)
        self.put('/core/personal/xp', str(new_xp))
        page.message('Character gains experience points. XP now: %s' % new_xp)
        next_level = self.next_level()
        if new_xp >= next_level:
            page.warning(self.level_up())
            page.error('Check for and apply manual increases to other stats if needed !')
        else:
            page.message('Next level at %s. %s experience points to go' % (next_level, next_level - new_xp))
        return new_xp

    def next_level(self):
        parentclass = self.get('/core/class/parent', '')
        childclass = self.get('/core/class/class', '')
        nl = int(self.get('/core/combat/level-hitdice', '')) + 1
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
        return self.equiped_by_type('weapon')

    def acquire_item(self, item):
        self()['core']['inventory']['pack'].append(item())

    def equip_item(self, itemname):
        slots = []
        has_unequiped = False
        for item in [Item(i) for i in self.get('/core/inventory/pack', [])]:
            if item.displayname == itemname:
                break
        if item:
            if item.itemtype() == 'armor' and not item.armortype() in self.get('/conditional/armor_types', ['cloth']):
                return (False, "%s cannot wear %s armor like %s" % (self.displayname(), item.armortype(), item.displayname()))
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
        return (True, "%s has equiped %s" % (self.displayname(), item.displayname()))

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

    def equiped_by_type(self, itemtype):
        arm = []
        equiped = self.get('/inventory/equiped', {})
        for slot in equiped:
            item = Item(equiped[slot])
            if item.itemtype == itemtype:
                arm.append(item)
        return arm

    def load_armor(self):
        return self.equiped_by_type('armor')

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
        conditionals = self.get('/conditionals/abilities', {})
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
