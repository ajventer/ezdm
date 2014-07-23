from util import readfile, save_json
from glob import glob
from simplejson import dumps
import sys
import os
from ezdm_libs import get_sys_data
      
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
           
    def filename(self,extension="json"):
        if extension:
            return "%s.%s" % (self.json['name'].replace(' ','_'),extension)
        else:
            return "%s" % (self.json['name'].replace(' ','_'))
       
    def save(self):
        save_json('items', self.filename(), self.json)
        open(os.path.join(get_user_data('items'),self.filename()),'w').write(dumps(self.json,indent=4))

    
    def displayname(self):
        return self.json['name']
    
    def itemtype(self):
        return self.json['type']
    


    
