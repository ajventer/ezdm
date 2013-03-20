import sys
import datetime
import os
from ezdm_libs import get_sys_data,gui,web
from simplejson import loads,dumps
from glob import iglob
from random import randrange
from pprint import pprint
if gui():
    import easygui as eg
if web():
    import cgi

def formheader(border=0):
    print "<form method=post>"
    print "<table border=%s>" %border
    
def formfooter():
    print '<tr><td colspan=2 align=center,valign=center><input type=submit name="submit"></td></tr></table>'
    print "</form>"
    
def webinput(description,name,default=''):
    print '<tr><td align=center valign=center><b>%s</b></td>' %(description)
    print "<td align=center valign=center>"
    if type(default) == type(''):
        print '<input type=text name="%s"></td></tr>'%name
    if type(default) == type([]):
        print '<select name="%s">' %name
        for item in default:
            print '<option>%s</option>' %item
        print '</select></td></tr>'
        
def dictinput(dic={},parent=None):
    for key in dic.keys():
        if not parent:
            name=key
        else:
            name="%s:%s" %(parent,key)
        if type(dic[key]) <> type({}):
            webinput(name,name,dic[key])
        else:
            dictinput(dic[key])
    
def cgiheader(title='',linkback=True):
    if len(title) == 0:
        t = title()
    else:
        t = title
    print "Content-type: text/html"
    print
    print "<html><head><title>%s</title></head><body>" %t
    print "<table width=100%><tr><td align=center bgcolor=lightgray><b>"
    print t
    print "</b>"
    if linkback:
        print "</td><td width=50 align=right>"
        print "<a href=ezdm.cgi><b>Home</b></a>"
        print "</td></tr><tr><td align=left>"
    else:
        print "</td></tr><tr><td>"

    
def cgifooter(linkback=True):
    if linkback:
        print "</td><td width=50 align=right valign=bottom>"
        print "<a href=ezdm.cgi><b>Home</b></a>"
    print "</td></tr></table>"
    print "</body></html>"    
    
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

def say(arg):
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
        output.append("<center><b> %s </b></center>" %(out))
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

def load_json(source=None,base=None,filename=None):
    if not filename:
        path=get_sys_data(source)
        if not path:
            path=get_user_data(source)
        f="%s.json" %base
        path=os.path.join(path,f)
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
            if m[lastkey] == test:
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
                    out[realkey]=smart_input(realkey,conditionals[conditional][key],validentries=control["validentries"],upper=control["upper"],lower=control["lower"],integer=control["integer"],decimal=control["decimal"])
        return out

def realkeys(template):
        rk=[]
        for key in template.keys():
            if key.startswith('__'):
                rk.append(key[3:])
            else:
                rk.append(key)
        return rk
    

def json_from_template(template={},old={},keypath="",conditional={}):    
    mydict={}
    for key in old.keys():
        if not key in realkeys(template):
            mydict[key]=old[key]
            
    for key in sorted(template.keys()):

        if key.startswith('__'):
            realkey=key[3:]
        else:
            realkey=key
        if keypath == "":
            showpath=realkey
        else:
            showpath="%s:%s" %(keypath,realkey)
        control=template_control(key,template[key])
        if key.startswith("__X"):
            if realkey in old:
                del old[realkey]
            if realkey in mydict:
                del mydict[realkey]
        elif key.startswith("__#"):
            if realkey in old:
                x=len(old[realkey])
            else:
                x=1
            numentries=smart_input("How many %s entries ?" %realkey,default=x,integer=True)
            subdic={}
            for I in range(0,numentries):
                try:
                    oldx=old[realkey][str(I)]
                except KeyError:
                    oldx={}
                subdic[str(I)]=json_from_template(template[key],oldx,"%s:%s" %(realkey,I))
            mydict[realkey]=subdic
        elif type(template[key]) == type({}):
            if realkey in old:
                mydict[realkey]=json_from_template(template[key],old[realkey],realkey)
            else:
                mydict[realkey]=json_from_template(template[key],{},realkey)
        elif realkey in old:
            mydict[realkey]=smart_input(showpath,old[realkey],validentries=control["validentries"],upper=control["upper"],lower=control["lower"],integer=control["integer"],decimal=control["decimal"])
        else:
            mydict[realkey]=smart_input(showpath,validentries=control["validentries"],upper=control["upper"],lower=control["lower"],integer=control["integer"],decimal=control["decimal"])
    
        
    if keypath == "":    
        mydict["conditionals"]=template_conditional(mydict,conditional)
    return mydict
        
            

def rolldice(auto=True,numdice=1,numsides=20,modifier=0,quiet=False):
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


