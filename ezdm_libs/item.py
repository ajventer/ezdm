from util import load_json
from glob import iglob,glob
from util import get_user_data
import sys
import os

def list_items(itemtype='all'):
    items={}
    for entry in iglob(os.path.join(get_user_data('items'),"*.json")):
        cname=os.path.basename(entry).rstrip('.json')
        item=Item(load_json('items',cname))
        if itemtype == 'all':
            items[item.displayname()] = cname
        elif item.itemtype() == itemtype:
            items[item.displayname()] = cname
    return items
        
class ItemEvents:
    json={}
    def __init__(self,name)
        self.json=load_json('items',name)
        
    def OnEquip(character={}):
        return character
    
    def OnDrop(character={}):
        return character
    
    def OnPickUp(character={}):
        return character
        
    def OnUse(character={},target={})
        return {"character":character,"target":target}
        
    

class Item:
    json={}
    events=None
    
    def __init__(self,name):
        self.json=load_json('items',name)
        sys.path.appened(get_user_data('items'))
        eventfile=os.path.join(get_user_data('items'),"name.py")
        if os.path.exists(eventfile):
            from name import Events
            events=Events()
        else:
            events=ItemEvents()
            
    def filename(self):
        return "%s.json" % self.json['name'].replace(' ','_')
    
    def save(self):
        open(os.path.join(get_user_data('items'),self.filename()),'w').write(dumps(self.json,indent=4))
        highlight('%s status saved to disk' %self.displayname(),clear=False)
    
    def displayname(self):
        return self.json['name']
    
    def itemtype(self):
        return self.json['type']
    


    
