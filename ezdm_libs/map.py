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
        maps[mymap.displayname()] = mymap.filename(None)
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
        for block in self.json['blocks']:
            if int(block["coordinates"]["x"]) == x and int(block["coordinates"]["y"]) == y:
                return block
        return None
    
    def setblock(self,x,y,block):
        current=self.block(x,y)
        block.json['coordinates']['x']=x
        block.json['coordinates']['y']=y
        if current:
            i=self.json['blocks'].index(current)
            self.json['blocks'][i] = block.json
        else:
            self.json['blocks'].append(block.json)
    
    def set_size(self,w,h):
        self.json['size']['w'] = w
        self.json['size']['h'] = h
        
    def fill(self,block=MapBlock()):
        w=int(self.json['size']['w'])
        h=int(self.json['size']['h'])
        for x in range(0,w):
            for y in range(0,h):
                if not self.block(x,y):
                    self.setblock(x,y,block)
    
    def displayname(self):
        return self.json['name']
        
    def filename(self,extension="json"):
        if extension:
            return "%s.%s" %(self.displayname().replace(' ','_'),extension)
        else:
            return "%s" %self.displayname().replace(' ','_')
    
    def drawblock(self,w,h,x,y,img,linkscheme):
        uri='/ezdm-iconview.cgi?icon=blank.png'
        if linkscheme:
            print '<a href="%s">' %linkscheme.replace('$x',str(x)).replace('$y',str(y))
        print '<img src="%s" width=%s height=%s>' %(uri,w,h)
        if linkscheme:
            print "</a>"
    
    def draw(self,sizex=700,sizey=500,border=0,linkscheme=None):
        w=int(self.json['size']['w'])
        h=int(self.json['size']['h'])
        blocksizex=int(sizex/(w))
        blocksizey=int(sizey/(h))
        print "<table border=%s cellpadding=0 cellspacing=0>" %border
        print "<tr><td bgcolor=lightgray align=center colspan=%s><b>%s</b></td></tr>" %(w +2,self.json['name'])
        print "<tr><td></td>"
        
        for x in range(0,w):
            print "<td>%s</td>" %x
        print "</tr>"
        for y in range(0,h):
            print "<tr><td>%s</td>" %y
            for x in range(0,w):
                has_something=self.block(x,y)
                if has_something:
                    block=MapBlock(has_something)
                    has_something=False
                    print '<td width=%s heigh=%s background="%s">' %(blocksizex,blocksizey,block.icon())
                    if len(block.characters()) > 0:
                        has_something=True
                        num=len(block.characters())
                        isizex=int(blocksizex/num)
                    for name in block.characters():
                        cjson = load_json('characters',name)
                        if 'icon' in cjson and len(cjson['icon']) >0:
                            uri='/ezdm-iconview.cgi?icon=%s' %json['icon']
                            print '<img src="%s" width=%s>' %(uri,isizex)
                    print "<br"
                    if len(block.items()) > 0:
                        has_something=True
                        num=len(block.items())
                        isizex=int(blocksizex/num)
                    for name in block.items():
                        cjson = load_json('items',name)
                        if 'icon' in cjson and len(cjson['icon']) >0:
                            self.drawblock(isizex,isizex,x,y,json['icon'],linkscheme)
                if not has_something:
                    print '<td width=%s heigh=%s >' %(blocksizex,blocksizey)
                    self.drawblock(blocksizex,blocksizey,x,y,'blank.png',linkscheme)
                print "</td>"
            print "</tr>"
        print "</table>"
            
    def save(self):
        outf=os.path.join(get_user_data('maps'),self.filename())
        open(outf,'w').write(dumps(self.json,indent=4))
        
                
    
        
