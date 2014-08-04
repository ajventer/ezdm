from util import rolldice, load_json
from math import hypot
import frontend


def range_mod(player, target):
    """
    Calculated the range modifier to misile attacks based on the
    ADnD manual's rules.
    """
    ploc = player.get('/core/location', {})
    tloc = target.get('/core/location', {})
    xdiff = ploc['x'] - tloc['x']
    ydiff = player['y'] - tloc['y']
    distance = hypot(xdiff, ydiff)
    if distance <= 1:
        #Short range
        return 0
    if distance <= 3:
        #Medium range
        return -2
    #long range
    return -5


def calc_damage(player, target):
    dmg_mod = player.dmg_mod()
    weapon = player.current_weapon()
    dmg = weapon.get('/conditional/dmg', 1)
    save = weapon.get('/conditional/save_against', 'none')
    if save != 'none':
        throw = target.saving_throw(save)
        if throw[0]:
            frontend.campaign.message(throw[1])
        return throw[0]
    damage = rolldice(numdice=1, numsides=dmg, modifier=dmg_mod)
    frontend.campaign.message('Rolling for damage: %s' % damage[1])
    taken = target.take_damage(damage[0])
    frontend.campaign.message(taken[1])
    return taken[0]


def attack(player, target, attack_modifiers):
    frontend.campaign.message('%s is attacking %s' % (player.displayname(), target.displayname()))
    target_alive = True
    attack_number = 1
    attack_mods = load_json('adnd2e', 'attack_mods')
    num_attacks = player.num_attacks()
    total_modifier = 0
    for mod in attack_modifiers:
        total_modifier += int(attack_mods[mod])
        frontend.campaign.message('Applying modifier %s: %s' % (mod, attack_mods[mod]))
    print "COMBAT: num_attacks:", num_attacks
    while attack_number <= num_attacks and target_alive:
        print "Attack number", attack_number, "Out of", num_attacks, "Target alive", target_alive
        weapon = player.current_weapon()
        frontend.campaign.message('Attacking with weapon %s' % weapon.displayname())
        if weapon.get('/conditional/weapon_type', 'melee') == 'misile':
            range_modifier = range_mod(player, target)
            if range_mod:
                frontend.campaign.message('Applying range modifier %s to misile weapon' % range_modifier)
                total_modifier += range_modifier
        frontend.campaign.message('Attack number %s out of %s' % (attack_number, num_attacks))
        attack_number += 1
        weaponmod = player.to_hit_mod()
        frontend.campaign.message('Applying weapon modifier %s' % weaponmod)
        total_modifier += weaponmod
        frontend.campaign.message('Total modifier: %s<br><br>' % total_modifier)
        attack_roll = player.attack_roll(target, total_modifier)
        frontend.campaign.message('Attack roll: %s %s %s' % (attack_roll[0], attack_roll[1], attack_roll[2]))
        if attack_roll[1] == 'Critical Hit !':
            frontend.campaign.message('Critical hit ! %s gain an extra attack.' % player.displayname())
            num_attacks += 1
        if attack_roll[1] == "Critical Miss !":
            frontend.campaign.message('Critical miss ! %s loses an attack.' % player.displayname())
            num_attacks - 1
        if "hit" in attack_roll[1].lower():
            if target.is_casting:
                target.interrupt_cast()
                frontend.campaign.message('%s was casting but it was interrupted by a successfull hit' % target.displayname)
            damage_result = calc_damage(player, target)
            target_alive = damage_result is True
            if not target_alive:
                if target.character_type() == 'npc':
                    for char in frontend.campaign.get('/core/players', []):
                        frontend.message(char.give_xp(target.xp_worth()))
                target.handle_death()
    for char in [player, target]:
        if char.character_type() == 'player':
            char.save()
        else:
            char.save_to_tile()
