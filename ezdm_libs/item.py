from util import load_json,get_set_icon
from glob import glob
from util import get_user_data,highlight
from simplejson import dumps
import sys
import os
from ezdm_libs import get_sys_data

def list_items(itemtype='all'):
    items={}
    itemfiles=glob(os.path.join(get_user_data('items'),"*.json"))    
    itemfiles+=glob(os.path.join(get_sys_data('items'),"*.json"))
    for entry in set(itemfiles):
        item=Item(load_json(filename=entry))
        if itemtype == 'all':
            items[item.displayname()] = item.filename(extension=None)
        elif item.itemtype() == itemtype:
            items[item.displayname()] = item.filename(extension=None)
    return items
        
class ItemEvents:
    json={}
    def __init__(self,json):
        self.json=json
        
    def OnEquip(self,character={}):
        return character

    def OnUnEquip(self,character={}):
        return character

    
    def OnDrop(self,character={}):
        return character
    
    def OnPickUp(self,character={}):
        return character
        
    def OnUse(self,character={},target={}):
        return {"character":character,"target":target}
        
class Item:
    json={}
    events=None
    def __init__(self,json):
        self.json=json
        sys.path.append(get_user_data('items'))
        eventfile=os.path.join(get_user_data('items'),self.filename('.py'))
        module=self.filename(None)
        if os.path.exists(eventfile):
            from module import Events
            events=Events(self.json)
        else:
            events=ItemEvents(self.json)

            
    def filename(self,extension="json"):
        if extension:
            return "%s.%s" % (self.json['name'].replace(' ','_'),extension)
        else:
            return "%s" % (self.json['name'].replace(' ','_'))
    
    def pprint(self,json,parent=None):
        out=[]
        for key in sorted(json.keys()):
            if not parent:
                name=key
            else:
                name="%s::%s" %(parent,key)
            if type(json[key]) <> type({}):
                out.append('<tr><td bgcolor=darkgray valign=top align=left>%s</td><td valign=top align=left>%s</td></tr>' %(name,json[key]))
            else:
                out += self.pprint(json[key],key)
        return out
                
            
    
    def viewitem(self):
        print "<table border=0 width=100%><tr><td valign=top>"
        print "<table width=100% border=2>"
        print '\n'.join(self.pprint(self.json))
        print "</table>"        
        print "</td><td valign=top>"
        get_set_icon('items',self.filename(None))
        print "</td></tr></table>"
  
    def save(self):
        print self.filename()
        open(os.path.join(get_user_data('items'),self.filename()),'w').write(dumps(self.json,indent=4))
        highlight('%s status saved to disk' %self.displayname(),clear=False)
    
    def displayname(self):
        return self.json['name']
    
    def itemtype(self):
        return self.json['type']
    


    
