#!/usr/bin/env python

from ezdm_libs.util import clearscr,smart_input,load_json,json_from_template,highlight,say,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,hide,template_conditional,validate_json
from ezdm_libs.character import Character,list_chars
from ezdm_libs.item import list_items,Item
from ezdm_libs import web,gui
import sys
import os

def view_inventory(character):
    
    output=[character.displayname(),'Items in pack:']
        
    for entry in character.list_inventory(['pack']):
        item=Item(load_json('items',entry))
        output.append('    %s' %item.displayname())
    output.append('')
    output.append('Items equiped:')
    for entry in character.list_inventory(['equiped']):
        item=Item(load_json('items',entry))
        output.append('    %s' %item.displayname())
    output.append('')
    output.append('Money:')
    output.append(character.list_money())
    return output

def select_item():       
    itemlist=list_items()
    if web():
        webinput("Select Item",'item',itemlist.keys())
        return
    selection=smart_input("Select Item",validentries=itemlist.keys())
    return itemlist[selection]
    
def select_from_inventory(character,section=['pack','equiped']):
    itemlist={}
    for i in character.list_inventory([section]):
        item=Item(load_json('items',i))
        itemlist[item.displayname()]=i
    if web():
        webinput('Item','item',itemlist.keys())
        return
    selected=smart_input('Select Item',validentries=itemlist.keys())
    return itemlist[selected]

def ask_money(action='add'):
    if not web():            
        gold=smart_input("Gold to %s" %action,default=0,integer=True)
        silver=smart_input("Silver to %s" %action,default=0,integer=True)
        copper=smart_input("Copper to %s" %action,default=0,integer=True)   
        return {"gold":gold,"silver":silver,"copper":copper}
    else:
        print """<table border=0'><tr><td bgcolor=lightgray>Money to %s:</td>
            <td>Gold: <input size=5 type=text name=moneygold value=0></td>
            <td>Silver: <input size=5 type=text name=moneysilver value=0></td>
            <td>Copper: <input size=5 type=text name=moneycopper value=0></td>
            </tr></table>""" %action

        

def main(actions):
    PATH = os.path.dirname(sys.argv[0])
    highlight('EZDM - Inventory Manager')
    clist=list_chars()
    if len(clist) == 0:
        sys.exit()
    name=smart_input("Select Character",upper=True,validentries=clist.keys()) 
    print name   
    json=load_json('characters',clist[name])
    character=Character(json,True) 
    MESSAGE=""
    action=""
    while action.upper() != "QUIT":
        clearscr()
        if len(MESSAGE) >0:
            highlight(MESSAGE,sayit=True)
            say(['',''])
            MESSAGE=''
        say(view_inventory(character))
        action=smart_input('Action',validentries=actions,upper=True)
        if action.upper() == "CREATE NEW ITEM":
            command="ezdm-mkitem"
            if not gui():
                command = command + ' --console'
            command=os.path.join(PATH,command)  
            os.system(command)
        if action.upper() == "ADD MONEY":
            money=ask_money()
            character.gain_money(money['gold'],money['silver'],money['copper'])
        if action.upper() == "REMOVE MONEY":
            money=ask_money('remove')
            if not character.spend_money(money['gold'],money['silver'],money['copper']):
                MESSAGE='Error: %s does not have enough money for that' %character.displayname()
        if action.upper() == "BUY ITEM":
            item=Item(load_json('items',select_item()))
            if not character.buy_item(item):
                MESSAGE='Error: %s cannot afford %s' %(character.displayname(),item.displayname())
        if action.upper() == 'ADD ITEM':
            item=Item(load_json('items',select_item()))
            character.acquire_item(item)
        if action.upper() == 'EQUIP ITEM':
            character.equip_item(select_from_inventory(character,'pack'))
        if action.upper() == 'UNEQUIP ITEM':
            character.unequip_item(select_from_inventory(character,'equiped'))
        if action.upper() == 'DROP ITEM':
            character.drop_item(select_from_inventory(character,'pack'))
            
    character.save()

def get_character():
    highlight("Select character to manage")
    formheader()
    webinput('Character:','character',list_chars().keys())
    formfooter()

def web_inventory(data,c):
    highlight('%s Current inventory' %c.displayname())
    print "<table border=5 width=80%><tr><td bgcolor=lightgray align=center>Pack</td><td bgcolor=lightgray>Equiped</td></tr>"
    print "<tr><td align=left>"
    say(c.list_inventory(['pack']))
    print "</td><td align=left>"
    say(c.list_inventory(['equiped']))    
    print "</td></tr>"
    print "<tr><td colspan=2 align=center bgcolor=lightgray>Money</td></tr>"
    print "<tr><td colspan=2>%s</td></tr>" %c.list_money() 
    print "</table>"
    return c
    
def do_action(data,character):
        formheader(title='%s' %(data['action']))
        hide('character',data['character'])
        hide('action',data['action'])
        hide('completeaction','yes')
        action=data['action']
        if action.upper() in ["ADD ITEM","BUY ITEM"]:
            select_item()
        if action.upper() in ["ADD MONEY","REMOVE MONEY"]:
            ask_money("%s" %action.lower().split()[0])
        if action.upper() in ["EQUIP ITEM" ,'DROP ITEM']:
            select_from_inventory(character,'pack')
        if action.upper() == "UNEQUIP ITEM":
            select_from_inventory(character,'equiped')       
        formfooter()

def completeaction(data,character):

    def load_item(itemname):
        return Item(load_json('items',list_items()[itemname]))
    
    highlight('Completing: %s' %(data['action']))
    action=data['action']
    if action.upper() == "ADD ITEM":
        character.acquire_item(load_item(data['item']))
    if action.upper() == "DROP ITEM":
        character.drop_item(list_items()[data['item']])
    if action.upper() == "EQUIP ITEM":
        character.equip_item(list_items()[data['item']])
    if action.upper() == "UNEQUIP ITEM":
        character.unequip_item(list_items()[data['item']])
    if action.upper() == "ADD MONEY":
        character.gain_money(int(data['moneygold']),int(data['moneysilver']),int(data['moneycopper']))
    if action.upper() == "REMOVE MONEY":
        character.spend_money(int(data['moneygold']),int(data['moneysilver']),int(data['moneycopper']))
    if action.upper()=="BUY ITEM":
        item=load_item(data['item'])
        if not character.buy_item(item):
            highlight('%s does not have enough money for %s' %(character.displayname(),item.displayname()))
        
    character.save()

def actionmenu(data):
    formheader(title='Action menu')
    hide('character',data['character'])
    del actions[actions.index('Quit')]
    del actions[actions.index("Create new item")]
    webinput('Action','action',actions)
    formfooter()

     
def webmain(actions):
    cgiheader('EZDM - Inventory Manager')
    data=parsecgi()
    if not 'character' in data:
        get_character()
        return
    else:
        cname=data['character']
        character=Character(load_json('characters',list_chars()[cname]),True)

    if not 'action' in data:
        actionmenu(data)
    elif not 'completeaction' in data:
         do_action(data,character)
    else:
        completeaction(data,character)
        actionmenu(data)
    web_inventory(data,character)
        
    cgifooter()
    
if __name__ == '__main__':
    actions=["Add item","Drop Item","Equip Item","Unequip Item","Create new item","Add money","Remove Money","Buy Item","Quit"]
    if web():
        webmain(actions)
    else:
        main(actions)
        
