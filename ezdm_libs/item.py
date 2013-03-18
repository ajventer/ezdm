from util import load_json
from glob import iglob
from util import get_user_data

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
        
    
    

class Item:
    json={}
    def __init__(self,name):
        self.json=load_json('items',name)
    
    def filename(self):
        return "%s.json" % self.json['name'].replace(' ','_')
    
    def save(self):
        open(os.path.join(get_user_data('items'),self.filename()),'w').write(dumps(self.json,indent=4))
        highlight('%s status saved to disk' %self.displayname(),clear=False)
    
    def displayname(self):
        return self.json['name']
    
    def itemtype(self):
        return self.json['type']
    
    def specialfx(self):
        #This will ultimately execute python in the field, with abilities to modify the in-memory copy of the character's json data
        pass


    
