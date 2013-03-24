import sys
import datetime
import os
from ezdm_libs import get_sys_data,gui,web
from simplejson import loads,dumps
from glob import iglob,glob
from random import randrange
from pprint import pprint
if gui():
    import easygui as eg
if web():
    import cgi
    

def formheader(border=5,title=None,wsgi=False,action=''):
    out=["<form method=post"]
    if len(action) > 0:
        out.append('action="%s"' %action)
    out.append("><table border=%s>" %border)
    if title:
        out.append("<tr><td colspan=2 bgcolor=darkgray>%s</td></tr>" %title)
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)
        
def select_char(characters,wsgi=False,):
    out=[]
    out.append(webinput('Character:','character',characters,wsgi=True))
  #  out.append(webinput('Use computer dice ?','autodice',['Yes','No'],wsgi=True))
    out.append(cgihide('autodice','Yes',wsgi=True))
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)
    
            
    
def formfooter(wsgi=False):
    out='<tr><td colspan=2 align=center,valign=center><input type=submit name="submit"></td></tr></table></form>'
    if wsgi:
        return out
    else:
        print out
    
def cgihide(name,value,wsgi=False):
    out='<input type=hidden name="%s" value="%s">' %(name,value)
    if wsgi:
        return out
    else:
        print out
    
def dicthide(dic={},wsgi=False):
    out=[]
    for key in dic.keys():
        out.append(cgihide(key,dic[key],wsgi=True))
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)
        
def webinput(description,name,default='',selected='',wsgi=False,hide=False):
    out=['<tr><td bgcolor=lightgray align=left valign=top><b>%s</b></td>' %(description)]
    out.append( "<td align=left valign=top>")
    if type(default) == type({}):
        dictinput(default,wsgi=wsgi,parent=selected,hide=hide)
    if type(default) == type(''):
        out.append('<input type=text name="%s" value="%s"></td></tr>'%(name,default))
    if type(default) == type([]):
        if not selected in default:
            out.append('<select name="%s">' %name)
        else:
            out.append( '<select name="%s" selected="%s">' %(name,selected))
            out.append( '<option>%s</option>' %selected)
        for item in default:
            out.append('<option>%s</option>' %item)
        out.append('</select></td></tr>')
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)
        
def dictinput(dic={},parent=None,wsgi=False,hide=False):
    out=[]
    for key in dic.keys():
        if not parent:
            name=key
        else:
            name="%s::%s" %(parent,key)
        if type(dic[key]) <> type({}):
            if not hide:
                out.append(webinput(name,name,dic[key],wsgi=True))
            else:
                out.append(cgihide(name,dic[key],wsgi=True))
                out.append('<tr><td bgcolor=lightgray align=left valign=center>%s</td><td align=center valign=center>%s</td></tr>'%(name,dic[key]))
        else:
            out.append(dictinput(dic[key],parent=name,hide=hide,wsgi=True))
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)
            
def cgiheader(title='',linkback=True,wsgi=False):
    if len(title) == 0:
        t = sys.argv[0]
    else:
        t = title
    out=[]
    if not wsgi:
        out.append("Content-type: text/html")
        out.append('')
    out += ["<html><head><title>%s</title></head><body>" %t,"<table width=100% border=0 cellpadding=0 cellspacing=0><tr><td align=center bgcolor=lightblue><b>",t,"</b>"]
    if linkback:
        out.append("</td><td width=50 align=right bgcolor=lightblue><a href=ezdm.cgi><b>Home</b></a></td></tr><tr><td align=left>")
    else:
        out.append("</td></tr><tr><td>")
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)    

    
def cgifooter(linkback=True,wsgi=False):
    out=[]
    if linkback:
        out.append("</td><td width=50 align=right bgcolor=lightblue valign=bottom><a href=ezdm.cgi><b>Home</b></a>")
    out.append("</td></tr></table></body></html>")
    if wsgi:
        return '\n'.join(out)
    else:
        print '\n'.join(out)    
            
def parsecgi():
    data={}
    form = cgi.FieldStorage()
    for key in form.keys():
        data[key]=form.getvalue(key)
    return data
    

def price_in_copper(gold,silver,copper):
    s=gold*10 + silver
    c=s*10+copper
    return c

def convert_money(copper):
    money={"gold":0,"silver":0,"copper":copper}
    while money['copper'] > 10:
        money['silver'] += 1
        money['copper'] -= 10
    while money['silver'] > 10:
        money['gold'] += 1
        money['silver'] -= 10
    return money
        

def clearscr():
    for X in range(0,100):
        print
        
def heal_dice(auto=True):
        sides=smart_input('Healing dice sides',validentries=dice_list(),integer=True)
        num=smart_input('Number of healing dice to roll',integer=True)
        return rolldice(auto,num,sides)        

def get_user_data(source):
    _ROOT=os.path.expanduser('~')
    _ROOT=os.path.join(_ROOT,'.ezdm')
    datapath=os.path.join(_ROOT,source)
    if not os.path.exists(datapath):
        os.makedirs(datapath)
    return  datapath

def title():
    return(os.path.basename(sys.argv[0]))

def say(arg,wsgi=False):
    if wsgi:
        if type(arg) == type(''):
            arg=[arg]
        return '<br>'.join(arg)
    
    if web():
        if type(arg) == type(''):
            arg=[arg]
        for line in arg:
            print "%s<br>" %line
                            
    return
    out=''
    if type(arg) == type([]):
        for line in arg:
            out='%s\n%s' %(out,line)
            print line
    else:
        out=arg
        print arg 
    if gui():
        eg.msgbox(out,title=title())

def highlight(out,clear=False,sayit=True):
    if clear:
        clearscr()
    bar=''
    output=[]
    if not web:
        output.append("# %s #" %(out))
    else:
        output.append('<center><table border=10 cellpadding=0 cellspacing=0><tr><td align=center valign=center bgcolor=darkgray>')
        output.append("<b> %s </b>" %(out))
        output.append('</td></tr></table></center>')
    if sayit:
        say(output)
    else:
        return output
    
def dice_list():
    return ['4','6','8','10','100','12','20']

def inrange(key1,key2):
        if '-' in key2:
            minimum=int(key2.split('-')[0])
            maximum=int(key2.split('-')[1])
        else:
            minimum=int(key2)
            maximum=minimum
        if int(key1) >= minimum and int(key1) <= maximum:
            return True
        else:
            return False

def get_set_icon(source='',base=''):
    json=load_json(source,base)
    print  "<table border=3><tr><td bgcolor=lightgray>Character Icon</td></tr>"
    if 'icon' in json and len(json['icon']) >0:
        uri='/ezdm-iconview.cgi?icon=%s' %json['icon']
        sys.stderr.write('Icon URI: %s \n' %uri )
        print '<tr><td><img src=%s width=100,height=100></td></tr>' %(uri)
    else:
        print "<tr><td>No icon configured</td></tr>"
    print "<tr><td bgcolor=lightgray>Select an icon</td></tr><tr><td>"
    print '<form method=post action="ezdm_seticon.cgi">'
    cgihide('source',source)
    cgihide('base',base)
    icons = glob(os.path.join(get_user_data('icons'),"*.*"))
    icons += glob(os.path.join(get_sys_data('icons'),"*.*"))
    icons= list(set(icons))
    for icon in sorted(icons):
        sys.stderr.write(icon)
        uri='/ezdm-iconview.cgi?icon=%s' %os.path.basename(icon)
        print '<input type=radio name=selected value="%s">' %os.path.basename(icon)
        print '<img width=50 src="%s"><br>%s<br>' %(uri,os.path.basename(icon))
    print '<input type=submit></form>'
    print "</td></tr>"
    print "<tr><td bgcolor=lightgray>Adding new icons:</td></tr><tr><td>"
    print '<tr><td width=100>To add your own<br>icons copy them into<br> <b>"%s"</b></td></tr>' %get_user_data('icons')
    print "</table>"
 

def serve_image(icon):
    imagetype=icon.split('.')[-1]
    sys.stderr.write("Content-type: image/%s\n" %imagetype)
    sys.stderr.write("Serving %s\n" %load_icon(icon))
    print "Content-type: image/%s\n" %imagetype
    print file(r"%s" %load_icon(icon), "rb").read()


def load_icon(icon='blank.png'):
    syspath=get_sys_data('icons')
    userpath=get_user_data('icons')
    path=''
    if os.path.exists(os.path.join(syspath,icon)):
        path=os.path.join(syspath,icon)
    if os.path.exists(os.path.join(userpath,icon)):
        path=os.path.join(userpath,icon) #User data overwrites system data if the same file exists in both
    if path=='':
        path=os.path.join(syspath,'blank.png')
    return path
    
        

def load_json(source=None,base=None,filename=None):
    if not filename:
        syspath=get_sys_data(source)
        userpath=get_user_data(source)
        f="%s.json" %base
        path=''
        if os.path.exists(os.path.join(syspath,f)):
            path=os.path.join(syspath,f)
        if os.path.exists(os.path.join(userpath,f)):
            path=os.path.join(userpath,f) #User data overwrites system data if the same file exists in both
        return loads(open(path,'r').read())
    else:
        return loads(open(filename,'r').read())

def template_control(key,value):
    control={"upper":False,"lower":False,"integer":False,"decimal":False,"validentries":[]}
    if key.startswith("__U"):
        control["upper"]=True
    if key.startswith("__L"):
        control["lower"]=True
    if key.startswith("__I"):
        control["integer"]=True
    if key.startswith("__D"):
        control["decimal"]=True     
    if str(value).startswith("__["):
        control["validentries"]=str(value).lstrip('__[').rstrip(']').split(',')   
    return control

def template_conditional(mydct={},conditionals={}):
        md=mydct
        out={}
        for conditional in conditionals.keys():
            condition,test=conditional.split("=")
            m=md
            lastkey=''
            for key in condition.split('.'):
                if key in m:
                    lastkey=key
                    if type(m[key]) == type({}):
                        m=m[key]
            if lastkey in m and m [lastkey] == test:
                for key in conditionals[conditional].keys():

                    if key.startswith('__'):
                        realkey=key[3:]
                    else:
                        realkey=key
                    control=template_control(key,conditionals[conditional][key])
                     
                    if "conditionals" in m and key in m["conditionals"]:
                        default=m["conditionals"][key]
                    else :
                        default=conditionals[conditional][key]
                    if not web():
                        out[realkey]=smart_input(realkey,conditionals[conditional][key],validentries=control["validentries"],upper=control["upper"],lower=control["lower"],integer=control["integer"],decimal=control["decimal"])
                    else:
                        realkey="conditionals::%s" %realkey
                        default=str(default)
                        if len(control['validentries']) == 0:
                            webinput(realkey,realkey,default)
                        else:
                            webinput(realkey,realkey,control['validentries'],default)
#                        print default

        return out

def realkeys(template):
        rk=[]
        for key in template.keys():
            if key.startswith('__'):
                rk.append(key[3:])
            else:
                rk.append(key)
        return rk

def samekeys(sw,dic):
    result={}
    for key in sorted(dic.keys()):
        if key.startswith(sw):
            result[key]=dic[key]
    return result
    
def recurse_colons(keys,old,parent):
    if not '::' in keys and len(keys) >0:       
        valuestring="%s::%s" %(parent,keys)
        s='"%s":"%s",' %(keys,old[valuestring])
        return s
    if len(keys) == 0:
        return ''
    
    firstkey=keys.split('::')[0]
    parentkey="%s::%s" %(parent,firstkey)
    t=''
    for sk in samekeys(parentkey,old):
        otherkeys='::'.join(sk.split(parentkey)[1:]).lstrip('::')
        t = '%s %s' %(t,recurse_colons(otherkeys,old,parentkey))
    t='"%s": {%s},' %(firstkey,t)
    return t
           
            

def validate_json(template={},old={}): 
    done=[]
    result={}
    for key in sorted(old.keys()):
        if '::' in key:   
            firstkey=key.split('::')[0]
            if firstkey in done:
                continue
            done.append(firstkey)
            s=''
            same=samekeys(firstkey,old)
            for sk in same.keys():
                otherkeys='::'.join(sk.split('::')[1:])
                ns=recurse_colons(otherkeys,old,firstkey) 
                if len(ns) > 0:
                    s="%s %s" %(s,ns)
            s=s.rstrip(',')
            s="{%s}" %s
            s=s.rstrip(',').replace(',}','}')
            result[firstkey]=loads(s)
        else:
            if not '{' in old[key]:
                result[key]=old[key]
            else:
                result[key] = loads(old[key].replace("'",'"'))
            
    return result
                

def json_from_template(template={},old={},parent="",conditional={}):    
    mydict={}
    if parent=="":
        for key in old.keys():
            if not key in realkeys(template):
                mydict[key]=old[key]
        if web():
            for key in mydict.keys():
                cgihide(key,mydict[key])

        
    for key in sorted(template.keys()):
        if key.startswith('__'):
            realkey=key[3:]
        else:
            realkey=key
        
        if parent=="":
            mypath=realkey
        else:
            mypath = "%s::%s" %(parent,realkey)

        control=template_control(key,template[key])
        if key.startswith("__X"):
            if realkey in old:
                del old[realkey]
            if realkey in mydict:
                del mydict[realkey]
            if realkey in old:
                x=len(old[realkey])
            else:
                x=1
        elif key.startswith('__Y'):
            if realkey in old:
                mydict[realkey] = old[realkey]
                webinput(mypath,mypath,old[realkey],selected=realkey,hide=True)
            else:
                mydict[realkey] = template[key]
                webinput(mypath,mypath,template[key],selected=realkey,hide=True)
        
        elif type(template[key]) == type({}):
                
            if realkey in old:
                mydict[realkey]=json_from_template(template[key],old[realkey],parent=mypath)
            else:
                mydict[realkey]=json_from_template(template[key],{},parent=mypath)
        elif realkey in old:
            if not web():
                mydict[realkey]=smart_input(mypath,old[realkey],validentries=control["validentries"],upper=control["upper"],lower=control["lower"],integer=control["integer"],decimal=control["decimal"])
            else:
                default=str(old[realkey])
                if len(control['validentries']) == 0:
                    webinput(mypath,mypath,default)
                else:
                    webinput(mypath,mypath,control['validentries'],default)
        else:
            if not web():
                mydict[realkey]=smart_input(mypath,validentries=control["validentries"],upper=control["upper"],lower=control["lower"],integer=control["integer"],decimal=control["decimal"])
            else:
                if len(control['validentries']) == 0:
                    default=str(template[key])
                else:
                    default=control['validentries']
                webinput(mypath,mypath,default)
    if parent == "":    
       if not web(): mydict["conditionals"]=template_conditional(mydict,conditional)
    return mydict
        
            

def rolldice(auto=True,numdice=1,numsides=20,modifier=0,quiet=False,wsgi=False):
        output=[]
        if not auto:
            return smart_input("Roll a %sd%s dice:" %(numdice,numsides),integer=True)
        else:
                total=0
                for I in range(1,numdice +1):
                        roll=randrange(1,numsides,1)
                        output.append("Rolled %s %s-sided dice: %s" %(I,numsides,roll))
                        total=total+roll
                
                total+=modifier       
                output.append("Total rolled: %s (modifier %s)" % (total,modifier))
                if not quiet:
                    say(output)
                if wsgi:
                    return (total,'<br>'.join(output))
                return total
                

def is_yesno(entries):
    yesno=True
    if len(entries) == 0:
        return False
    for item in entries:
        if item.lower() not in ['y','n']:
            yesno=False
    return yesno

def smart_input(message='',default=None,integer=False,decimal=False,validentries=[],indent=0,lower=False,upper=False,confirm=''):      
    if len(validentries) == 1:
        return validentries[0]
    print
    error="no input"
    istr=""
    for I in range(0,indent):
        istr=" %s" %istr
    istr=''
    while error <> '':
        if error <> '' and error <> "no input":
            eg.exceptionbox("%s%s%s" %(istr,istr,error),title=title())
        error=''
        printmessage=message
        printmessage="%s%s" %(istr,printmessage)
        if default:
            printmessage="%s (%s)" %(printmessage,default)
        if len(validentries) > 0:
            for entry in validentries:
                print "%s%s (%s): %s" %(istr,istr,validentries.index(entry)+1,entry)       
        print "%s ?" %printmessage,
        if gui():
            user_input=None
            if is_yesno(validentries):
                if eg.ynbox(printmessage,title=title()) == 1:
                    user_input='y'
                else:
                    user_input='n'
            elif len(validentries) == 1:
                user_input=eg.boolbox(printmessage,title=title(),choices=validentries)
            elif len(validentries) > 1:
                while user_input == None:
                    user_input=eg.choicebox(printmessage,title=title(),choices=validentries)
            else:
                if integer or decimal:
                    while user_input == None:
                        user_input=eg.integerbox(printmessage,title=title(),default=default)
                else:
                    while user_input == None:
                        user_input=eg.enterbox(printmessage,title=title(),default=default)
        else:
            user_input=raw_input()     
        if len(validentries) > 0:
            try:
                select=validentries[int(user_input) -1]
            except:
                select=user_input
            user_input=select          
            if not user_input in validentries:
                error='Error: entry not in list'        
        if lower:
            user_input=user_input.lower()
        if upper:
            user_input=user_input.upper()
        if default and user_input == '':
            user_input=default
        if integer:
            try:
                user_input = int(user_input)
            except Exception as E:
                error='Error:  %s' %E
        elif decimal:
            try:
                user_input = float(user_input)
            except Exception as E:
                error='Error:  %s' %E

        if len(confirm) > 0:
            if smart_input(confirm.replace('%I',user_input),default='n',validentries=['y','n'],indent=indent,lower=True) == 'y':
                return user_input
            else:
                error="Not confirmed - retrying"
        else:
            return user_input
 
def strtodic(s):
    """ Turns strings in format k1:v1,k2:v2,k3:v3 into dictionaries """
    D={}
    s = s.lstrip('{').rstrip('}') #If there are outer brackets, ignore them
    for pair in s.split(','):
        if ':' in pair: 
            K,V=pair.partition(':')[0],pair.partition(':')[2]
            D[K] = V
    return D
        

def option(optionx,expect=None):
    """ return an option from the parameter list if it exists """
    value = None
    paramlist=sys.argv
    if type(optionx) == int:
        # numbered parameter - return if available
        if len(paramlist) > optionx:
            value = paramlist[optionx]
    elif type(optionx) == str:
        # look for a string named optionx and pop it if found
        for p in range(len(paramlist)):
            if paramlist[p].lower().startswith(optionx.lower()):
                if len(paramlist[p]) > len(optionx) and paramlist[p][len(optionx)] == '=':
                    value = paramlist.pop(p)[len(optionx)+1:]
                else:
                    value = paramlist.pop(p) and True
                break
    if expect and expect == 'json' and value:
        try:
            value = loads(value)
        except Exception,e:
            print "util.option: invalid json format"
            value = None
    return value


