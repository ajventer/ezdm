from util import load_json,inrange,get_user_data
import os
from simplejson import dumps
from character import Character
from item import Item
from glob import glob
from ezdm_libs import get_sys_data

def list_maps():
    maps={}
    mapfiles=glob(os.path.join(get_user_data('maps'),"*.json"))    
    mapfiles+=glob(os.path.join(get_sys_data('maps'),"*.json"))
    if len(set(mapfiles)) == 0:
        return {}
    for entry in set(mapfiles):
        mymap=Map(load_json(filename=entry))
        maps[entry] = mymap.displayname()
    return maps
        

class MapBlock:
    json={"coordinates":{"x":0,"y":0},
            "characters":[],
            "items":[],
            "can_enter":True,
            "icon":"blank.png",
            "link":{"map":None,"x":0,"y":0}
            }
    def __init__(self,json=None):
        if json:
            self.json = json
            
    def icon(self):
         uri='/ezdm-iconview.cgi?icon=%s' %self.json['icon']
         return uri
         
    
    def characters(self):
        return self.json['characters']
        
    def items(self):
        return self.json['items']
        
    def add(self,characters=[],items=[]):
        if len(characters) > 0:
            if type (characters) == type ([]):
                self.json['characters'] += characters
            else:
                self.json['characters'].append(characters)
        if len(items) >0:
            if type(items) == type([]):
                self.json['items'] += items
            else:
                self.json['items'].append(items)
    
    def remove(self,characters=[],items=[]):
        if len(characters) > 0:
            if type(characters) == type([]):
                self.json['characters'] -= characters
            else:
                i=self.json['characters'].index(characters)
                del self.json['characters'][i]
        if len(items) > 0:
            if type(items) == type([]):
                self.json['items'] -= items
            else:
                i=self.json['items'].index(items)
                del self.json['items'][i]
                
    def can_enter(self):
        return self.json['can_enter']
    
    def link(self):
        if not self.json['link']['map']:
            return None
        else:
            return self.json['link']
            
class Map:
    json={"name":"",
         "size":{"w":1,"h":1},
         "blocks":[]
        }
    def __init__(self,json=None):
        if json:
            self.json=json
    
    def block(self,x,y):
        for key in self.json['blocks']:
            if int(self.json[key]["coordinates"]["x"]) == x and int(self.json[key]["coordinates"]["y"]) == y:
                return MapBlock(self.json[key])
        return None
    
    def setblock(self,x,y,block):
        current=self.block(x,y)
        if current:
            i=self.json['blocks'].index(current)
            self.json['blocks'][i] = block
        else:
            self.json['blocks'].append(block)
    
    def set_size(self,w,h):
        self.json['size']['w'] = w
        self.json['size']['h'] = h
        
    def fill(self,block=MapBlock()):
        w=int(self.json['size']['w'])
        h=int(self.json['size']['h'])
        for x in range(0,w):
            for y in range(0,h):
                setblock(x,y,block)
    
    def displayname(self):
        return self.json['name']
        
    def filename(self,extension="json"):
        if extension:
            return "%s.%s" %(self.displayname().replace(' ','_'),extension)
        else:
            return "%s" %self.displayname().replace(' ','_')
            
    def draw(self,sizex=700,sizey=500,border=0):
        w=int(self.json['size']['w'])
        h=int(self.json['size']['h'])
        blocksizex=int(sizex/w)
        blocksizey=int(sizey/h)
        print "<table border=%s cellpadding=0 cellspacing=0>" %border
        print "<tr><td bgcolor=lightgray align=center colspan=%s><b>%s</b></td></tr>" %(h,self.json['name'])
        for y in range(0,h):
            print "<tr>"
            for x in range(0,w):
                has_something=self.block(x,y)
                if has_something:
                    has_something=False
                    print '<td width=%s heigh=%s background="%s">' %(blocksizex,blocksizey,self.block(x,y).icon())
                    if len(self.block(x,y).characters()) > 0:
                        has_something=True
                        num=len(self.block(x,y).characters())
                        isizex=int(blocksizex/num)
                    for name in self.block(x,y).characters():
                        cjson = load_json('characters',name)
                        if 'icon' in cjson and len(cjson['icon']) >0:
                            uri='/ezdm-iconview.cgi?icon=%s' %json['icon']
                            print '<img src="%s" width=%s>' %(uri,isizex)
                    print "<br"
                    if len(self.block(x,y).items()) > 0:
                        has_something=True
                        num=len(self.block(x,y).items())
                        isizex=int(blocksizex/num)
                    for name in self.block(x,y).items():
                        cjson = load_json('items',name)
                        if 'icon' in cjson and len(cjson['icon']) >0:
                            uri='/ezdm-iconview.cgi?icon=%s' %json['icon']
                            print '<img src="%s" width=%s>' %(uri,isizex)
                if not has_something:
                    print '<td width=%s heigh=%s >' %(blocksizex,blocksizey)
                    uri='/ezdm-iconview.cgi?icon=blank.png'
                    print '<img src="%s" width=%s height=%s>' %(uri,blocksizex,blocksizey)
                print "</td>"
            print "</tr>"
        print "</table>"
            
    def save(self):
        outf=os.path.join(get_user_data('maps'),self.filename())
        open(outf,'w').write(dumps(self.json))
        
                
    
        
