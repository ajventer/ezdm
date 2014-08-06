from util import inflate, flatten, rolldice, inrange, price_in_copper, convert_money, save_json, load_json, readkey, writekey
from item import Item
from objects import EzdmObject, event
from gamemap import GameMap
import copy
from random import randrange
import frontend


class Character(EzdmObject):
    removed = False
    json = {}
    auto = False
    index = -1
    weapon = 0

    def __init__(self, json):
        self.json = json
        if self.json:
            if not self.character_type() == 'player':
                numdice = int(self.get('/core/combat/level-hitdice', '1'))
                self.put('core/combat/hitpoints', rolldice(numdice=numdice, numsides=8)[0])
                self.put('core/combat/max_hp', numdice * 8)

    def handle_death(self):
        loc = self.location()
        print "Dead character was at %s" % loc
        chartype = self.character_type()
        if chartype == 'player':
            chartype = 'players'
            todel = self.name()
        else:
            chartype = 'npcs'
            todel = self.get_tile_index()
        gamemap = GameMap(load_json('maps', loc['map']))
        gamemap.removefromtile(loc['x'], loc['y'], todel, chartype)
        print chartype
        if chartype == 'npcs':
            max_gold = self.get('/conditional/loot/gold', 0)
            max_silver = self.get('/conditional/loot/silver', 0)
            max_copper = self.get('/conditional/loot/copper', 0)
            loot_items = self.get('/conditional/loot/items_possible', [])
            max_items = self.get('/conditional/loot/max_items', 1)
            always_drops = self.get('/conditional/loot/always_drops', [])
            gold = rolldice(1, max_gold, 0)[0]
            silver = rolldice(1, max_silver, 0)[0]
            copper = rolldice(1, max_copper, 0)[0]
            print "Dropping money %s - %s - %s" % (gold, silver, copper)
            for counter in range(0, max_items):
                item = None
                print "Potential drop: %s of %s" % (counter, max_items)
                drops_item = rolldice(1, 100, 0)[0]
                print "Drop-roll: %s" % drops_item
                if loot_items and drops_item > 50:
                    print "Select random item from to drop from %s" % loot_items
                    item = loot_items[randrange(0, len(loot_items) - 1)]
                if item:
                    print "Item dropped %s" % item
                    gamemap.addtotile(loc['x'], loc['y'], item, 'items')
            print "Always drops: %s" % always_drops
            for item in always_drops:
                print "Dropping %s" % item
                gamemap.addtotile(loc['x'], loc['y'], item, 'items')
            gamemap.putmoney(loc['x'], loc['y'], gold, silver, copper)
        gamemap.save()
        frontend.campaign.chars_in_round()

    def location(self):
        return self.get('/core/location', {})

    @property
    def lightradius(self):
        base_radius = self.get('/core/lightradius', 0)
        for item in self.inventory_generator():
            if item[1].get('/core/in_use', False):
                base_radius += item[1].get('/core/lightradius', 0)
        return base_radius

    def memorized_spells(self):
        result = {}
        spells = self.get('/core/inventory/spells', [])
        for idx in self.get('/core/inventory/spells_memorized', []):
            try:
                item = spells[idx]
                level = item.get('/conditional/spell_level', 1)
                if not level in result:
                    result[level] = []
                result[level].append(idx)
            except:
            # once inventory updates are reliable - remove this try/except
                pass
        return result

    def moveto(self, mapname, x, y, page=None):
        if not mapname:
            return
        if not isinstance(x, int) or not isinstance(y, int):
            try:
                x = int(x)
                y = int(y)
            except:
                return
        current = self.location()
        print current
        if current.get('map'):
            gamemap = GameMap(load_json('maps', current['map']))
            gamemap.removefromtile(current['x'], current['y'], self.name(), 'players')
            print "Saving", gamemap.save()
        self.put('/core/location/x', x)
        self.put('/core/location/y', y)
        self.put('/core/location/map', mapname)
        self.save()
        gamemap = GameMap(load_json('maps', mapname))
        gamemap.addtotile(x, y, self.name(), 'players')
        if page:
            tile = gamemap.tile(x, y)
            tile.onenter(self, page)
            gamemap.load_tile_from_json(x, y, tile())
        if self.character_type() == 'player':
            gamemap.reveal(x, y, self.lightradius)
        print "Saving", gamemap.save()

    def inventory_generator(self, sections=['pack', 'equiped', 'spells']):
        for section in sections:
            items = self.get('/core/inventory/%s' % section, [])
            idx = -1
            if isinstance(items, list):
                for item in items:
                    idx += 1
                    yield (section, Item(item), idx)
            elif isinstance(items, dict):
                for k, v in items.items():
                    yield (k, Item(v), 0)
            else:
                self.put('/core/inventory/%s', [])

    @property
    def is_casting(self):
        for item in self.inventory_generator():
            if item[1].get('/core/in_use', False):
                return True
        return False

    def interrupt_cast(self):
        for item in self.inventory_generator():
            if item[1].get('/core/in_use', False):
                item[1].interrupt_cast()
            if item[0] in ['spells', 'pack']:
                self()['core']['inventory'][item[0]][item[2]] = item[1]()
            else:
                self.put('/core/inventory/equiped_by_type/%s' % item[0], item[1]())

    def character_type(self):
        return self.get('/core/type', 'player')

    def oninteract(self, target, page):
        event(self, '/conditional/events/oninteract', {'character': self, 'page': page, 'target': target})

    def remove_from_combat(self):
        self.removed = True

    def xp_worth(self):
        xpkey = self.get('core/combat/level-hitdice', 1)
        print xpkey
        xpvalues = load_json('adnd2e', 'creature_xp.json')
        print xpvalues
        if str(xpkey) in xpvalues.keys():
            xp = xpvalues[str(xpkey)]
        elif int(xpkey) > 12:
            xp = 3000 + ((int(xpkey) - 13) * 1000)
        return int(xp)

    def set_index(self, index):
        self.index = index

    def set_tile_index(self, index):
        self.put('/core/tileindex', index)

    def save_to_tile(self):
        loc = self.location()
        gamemap = GameMap(load_json('maps', loc['map']))
        gamemap.tile(loc['x'], loc['y'])()['conditional']['npcs'][self.get_tile_index()] = self()

    def get_tile_index(self):
        return self.get('/core/tileindex', -1)

    def heal(self, amount):
        hp = int(self.get('/core/combat/hitpoints', 1))
        hp += amount
        if hp > int(self.get('/core/combat/max_hp', 1)):
            self.put('/core/combat/hitpoints', int(self.get('/core/combat/max_hp', 1)))
        else:
            self.put('/core/combat/hitpoints', hp)
        return self.get('/core/combat/hitpoints', 1)

    def take_damage(self, damage):
        out = ''
        if damage >= self.get('/core/combat/hitpoints', 1):
            st = self.saving_throw('ppd')
            out = '<br>'.join(st[1])
            if not st[0]:
                self.put('/core/combat/hitpoints', 0)
                out += "<br>%s has died !" % self.displayname()
                return (False, out)
            else:
                self.put('/core/combat/hitpoints', 1)
                out += "<br>%s barely survives. %s hitpoints remaining" % (self.displayname(), self.get('/core/combat/hitpoints', 1))
                return (True, out)
        else:
            hp = int(self.get('/core/combat/hitpoints', 1))
            hp -= damage
            self.put('/core/combat/hitpoints', hp)
            out += "<br>%s takes %s damage. %s hitpoints remaining" % (self.displayname(), damage, self.get('/core/combat/hitpoints', 1))
            return (True, out)

    def name(self):
        name = '%s_%s.json' % (self.get('/core/personal/name/first', ''), self.get('/core/personal/name/last', ''))
        return name.lower()

    def save(self):
        print "Saving %s to disk" % self.displayname()
        self.json = inflate(flatten(self.json))
        if 'temp' in self():
            del self()['temp']
        if frontend.campaign:
            print "Updating campaign"
            frontend.campaign.chars_in_round()
        return save_json('characters', self.name(), self.json)

    def to_hit_mod(self):
        ability_mods = load_json('adnd2e', 'ability_scores')
        strength = self.get('/core/abilities/str', 1)
        base = int(readkey('/str/%s/hit' % strength, ability_mods, 0))
        if len(self.weapons) > 0:
            bonus = int(readkey('/conditionals/to_hit', self.weapons[self.weapon](), 0))
        else:
            bonus = 0
        return base + bonus

    def ppd_mod(self):
        ability_mods = load_json('adnd2e', 'ability_scores')
        con = self.get('/core/abilities/con', 1)
        return int(readkey('/con/%s/ppd' % con, ability_mods))

    def dmg_mod(self):
        ability_mods = load_json('adnd2e', 'ability_scores')
        strength = self.get('/core/abilities/str', 0)
        return int(readkey('/str/%s/dmg' % strength, ability_mods, 0))

    def def_mod(self):
        ability_mods = load_json('adnd2e', 'ability_scores')
        dex = self.get('/core/abilities/dex', 0)
        return int(readkey('/dex/%s/defense' % dex, ability_mods, 0))

    @property
    def saving_throws(self):
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
        target = int(readkey(against, self.saving_throws, 0))
        out = "%s Tries to roll a saving throw against %s" % (self.displayname(), prettyname)
        out += "<br>%s needs to roll %s" % (self.displayname(), target)
        roll = rolldice(numdice=1, numsides=20, modifier=mod)
        out += '<br>%s' % roll[1]
        if roll[0] >= int(target):
            out += '<br>Saved !'
            return (True, out)
        else:
            out += "<br>Did not save !"
            return (False, out)

    def hit_dice(self):
        if self.is_monster():
            return int(self.get('/core/combat/level-hitdice', 1))
        else:
            return 1

    def autoroll(self):
        return self.auto

    def current_weapon(self):
        return self.weapons[self.weapon]

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
        self.__init__(self())
        return out

    def give_xp(self, xp):
        current_xp = int(self.get('/core/personal/xp', 0))
        new_xp = current_xp + int(xp)
        self.put('/core/personal/xp', str(new_xp))
        frontend.campaign.message('%s gains %s experience points. XP now: %s' % (self.displayname(), xp, new_xp))
        next_level = self.next_level()
        if new_xp >= next_level:
            frontend.campaign.warning(self.level_up())
            frontend.campaign.error('Check for and apply manual increases to other stats if needed !')
        else:
            frontend.campaign.message('Next level at %s. %s experience points to go' % (next_level, next_level - new_xp))
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
        frontend.campaign.message('%s has THAC0 of: %s' % (self.displayname(), self.thac0))
        target_stats = '%s has a defense modifier of %s and armor class %s' % (target.displayname(), target.def_mod(), target.armor_class())
        frontend.campaign.message(target_stats)
        target_roll = self.thac0 - target.armor_class() - target.def_mod()
        frontend.campaign.message('%s needs to roll %s to hit %s' % (self.displayname(), target_roll, target.displayname()))
        roll = rolldice(numdice=1, numsides=20, modifier=mod)
        if roll[0] - mod == 1:
                return (roll[0], "Critical Miss !", roll[1])
        elif roll[0] - mod == 20:
            return (roll[0], "Critical Hit !", roll[1])
        else:
            if roll[0] >= target_roll:
                return (roll[0], "Hit !", roll[1])
            else:
                return (roll[0], "Miss !", roll[1])

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
        weapons = self.equiped_by_type('weapon')
        if not weapons:
            fist = Item(load_json('items', 'fist.json'))
            self.acquire_item(fist)
            self.equip_item(fist.name())
        weapons = self.equiped_by_type('weapon')
        return weapons

    def learn_spell(self, spellitem):
        spells = self.get('/core/inventory/spells', [])
        if not isinstance(spells, list):
            self.put('/core/inventory/spells', [])
        spellitem.identify()
        self()['core']['inventory']['spells'].append(spellitem())

    def unlearn_spell(self, index):
        del(self()['core']['inventory']['spells'][index])

    def acquire_item(self, item):
        if not isinstance(self.get('/core/inventory/pack', []), list):
            self.put('/core/inventory/pack', [])
        self()['core']['inventory']['pack'].insert(0, item())

    def equip_item(self, itemname):
        slots = []
        canwear = self.get('/conditional/armor_types', 0)
        armor_types = load_json('adnd2e', 'armor_types.json')
        shields = self.get('/conditional/shields', False)

        has_unequiped = False
        if isinstance(itemname, int):
            item = Item(self.get('/core/inventory/pack', [])[itemname])
        else:
            for item in [Item(i) for i in self.get('/core/inventory/pack', [])]:
                if item.displayname == itemname:
                    break
        if not item.identified():
            item.identify()
        if item:
            if item.armortype() == 'shield' and not shields:
                return (False, "%s cannot wear %s shields like %s" % (self.displayname(), item.armortype(), item.displayname()))
            elif item.armortype() != 'shield' and item.itemtype() == 'armor' and not armor_types[item.armortype()] > canwear:
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
                if self.get('/core/inventory/equipped/%s' % item.slot().strip(), {}) and not has_unequiped:
                    self.unequip(slot)
                    #Prevent equipping over a twohander from duplicatng it
                    has_unequiped = True
                self.put('/core/inventory/equiped/%s' % slot.strip(), item())
                self.drop_item(item.displayname())
        return (True, "%s has equiped %s" % (self.displayname(), item.displayname()))

    def unequip_item(self, slot):
        slot = slot.strip()
        print slot
        current = self.get('/core/inventory/equiped/%s' % slot, {})
        print current
        if current:
            self.json['core']['inventory']['pack'].append(current)
        self.put('/core/inventory/equiped/%s' % slot, {})

    def sell_price(self, gold, copper, silver):
            price = price_in_copper(gold, silver, copper)
            print price
            cha = int(self.get('/core/abilities/cha', 1))
            price = (price / 2) + ((price / 100) * cha)
            print price
            money = convert_money(price)
            print money
            return (money['gold'], money['silver'], money['copper'])

    def sell_item(self, itemname, buyer='shop', gold=0, silver=0, copper=0):
        if isinstance(itemname, int):
            tosell = Item(self.get('/core/inventory/pack', [])[itemname])
        else:
            for item in self.get('/core/inventory/pack', []):
                if item.displayname() == itemname:
                    tosell = Item(item)
                    break
        if buyer != 'shop':
            buyer.spend_money(gold, silver, copper)
            buyer.acquire_item(tosell())
        else:
            gold, silver, copper = self.sell_price(*tosell.price_tuple())

        self.drop_item(itemname)
        self.gain_money(gold, silver, copper)

    def for_sale(self):
        out = []
        pack = self.get('/core/inventory/pack', [])
        for i in pack:
            item = Item(i)
            if item.name() != '.json':
                gold, silver, copper = self.sell_price(*item.price_tuple())
                moneystr = 'Gold %s, Silver %s, Copper %s' % (gold, silver, copper)
                out.append((pack.index(i), item.displayname(), moneystr))
        return out

    def drop_item(self, itemname, section='pack'):
        todrop = None
        if isinstance(itemname, str):
            for item in self.get('/core/inventory/%s' % section, []):
                item = Item(item)
                if item.displayname() == itemname:
                    todrop = self.get('/core/inventory/%s' % section, []).index(item())
        else:
            todrop = itemname
        if todrop is None:
            return
        item = Item(self.json['core']['inventory']['pack'][todrop])
        item.ondrop(player=self)
        del(self.json['core']['inventory']['pack'][todrop])

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

    def buy_item(self, item, page=None):
        if self.spend_money(*item.price_tuple()):
            self.acquire_item(item)
            page.message('You bought a %s' % item.name())
            return True
        else:
            page.error('You cannot afford to buy %s' % item.name())
            return False

    def gain_money(self, gold=0, silver=0, copper=0):
        total_gained = price_in_copper(gold, silver, copper)
        my_total = price_in_copper(*self.money_tuple())
        my_total += total_gained
        self.put('/core/inventory/money', convert_money(my_total))

    def armor_class(self):
        AC = 10.0
        for item in self.equiped_by_type('armor'):
            AC -= float(readkey('/conditional/ac', item(), 0.0))
        return AC

    def equiped_by_type(self, itemtype):
        arm = []
        equiped = self.get('/core/inventory/equiped', {})
        for slot in equiped:
            item = Item(equiped[slot])
            if item.itemtype() == itemtype:
                arm.append(item)
        return arm

    @property
    def armor(self):
        return self.equiped_by_type('armor')

    @property
    def weapons(self):
        return self.equiped_by_type('weapon')

    def num_weapons(self):
        return len(self.weapons)

    def num_attacks(self):
        atr_json = load_json('adnd2e', 'various')
        atr = readkey('/various/attacks_per_round', atr_json)
        print atr
        parentclass = self.get('/core/class/parent', '')
        print "Parent class:", parentclass
        if not parentclass in atr:
            ATR = 1
        else:
            for key in atr[parentclass].keys():
                print "Checking", key
                if inrange(self.get('/core/combat/level-hitdice', 1), key):
                    print "Matched !"
                    ATR = int(atr[parentclass][key])
                    print "Base ATR", ATR
        print "Num weapons", self.num_weapons()
        return self.num_weapons() * int(ATR)

    def current_xp(self):
        return int(self.get('/core/personal/xp', 0))

    def tryability(self, ability, modifier=0):
        out = ['%s is trying to %s' % (self.displayname(), ability)]
        target_roll = int(self.abilities()[ability])
        target_roll += int(modifier)
        out.append('%s must roll %s or lower to succeed' % (self.displayname(), target_roll))
        roll = rolldice(numdice=1, numsides=100)
        out.append(roll[1])
        if roll[0] <= target_roll:
            return (True, out)
        else:
            return (False, out)

    def abilities(self):
        subclass = self.get('/core/class/class', '')
        parentclass = self.get('/core/class/parent', '')
        level = self.get('/core/combat/level-hitdice', '')
        various = load_json('adnd2e', 'various')
        abilities = various['abilities']
        conditionals = self.get('/conditional/abilities', {})
        print conditionals
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
        if self.index > -1 and self.character_type() == 'npc':
            out = "%s (%s)" % (out, self.index)
        out = "[%s]" % out
        return out

    @property
    def thac0(self):
        if self.get('/core/personal/race', '') == "creature":
            key = "creature"
        else:
            key = self.get('/core/class/parent', '')
        thac0s = load_json("adnd2e", "thac0")[key]
        for key2 in thac0s.keys():
            if inrange(self.get('/core/combat/level-hitdice', 1), key2):
                return int(thac0s[key2])

    def render(self):
        out = copy.deepcopy(self())
        out['core']['lightradius'] = self.lightradius
        prettynames = load_json('adnd2e', 'saving_throws')
        writekey('/conditional/abilities', self.abilities(), out)
        if not self.character_type() == 'player':
            out['XP Worth'] = self.xp_worth()
        if 'saving_throws' in out['core']['combat']:
            del out['core']['combat']['saving_throws']
        for k, v in self.saving_throws.items():
            prettyname = readkey('/names/%s' % k, prettynames, k)
            writekey('/core/combat/saving_throws/%s ' % prettyname, v, out)
        self.reset_weapon()
        out['core']['combat']['armor_class'] = self.armor_class()
        out['to_hit_mod'] = {}
        done = False
        if self.weapons:
            for I in range(0, len(self.weapons)):
                self.next_weapon()
                name = self.weapons[self.weapon].get('/core/name', '')
                writekey('/to_hit_mod/%s' % name, self.to_hit_mod(), out)
                if self.weapon == 0:
                    if done:
                        break
                    else:
                        done = True
        del(out['core']['inventory'])
        return out
