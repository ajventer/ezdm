import sys
import datetime
#import envoy
import syslog
import os
from pwd import getpwnam
from grp import getgrnam
from simplejson import loads

def load_json(source=None,base=None,filename=None):
    if not filename:
        return loads(open("%s/%s.json" %(source,base),'r').read())
    else:
        return loads(open(filename,'r').read())

def json_from_template(template={},old={},keypath=""):
    mydict={}
    for key in template.keys():
        upper=False
        lower=False
        validentries=[]
        if key.startswith('__'):
            realkey=key[3:]
        else:
            realkey=key
        if keypath == "":
            showpath=realkey
        else:
            showpath="%s:%s" %(keypath,realkey)
        if key.startswith("__U"):
            upper=True
        if key.startswith("__L"):
            lower=True
               
        if str(template[key]).startswith("__["):
            validentries=str(template[key]).lstrip('__[').rstrip(']').split(',')
        if key.startswith("__#"):
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
            mydict[realkey]=smart_input(showpath,old[realkey],validentries=validentries,upper=upper,lower=lower)
        else:
            mydict[realkey]=smart_input(showpath,validentries=validentries,upper=upper,lower=lower)
    return mydict
        
            

def rolldice(auto=True,numdice=1,numsides=20,modifier=0):
        print
        if not auto:
                while True:
                        print "Roll a %sd%s dice:"
                        try:
                                return int(raw_input())
                        except:
                                print "Error you must enter a number"
        else:
                total=0
                for I in range(1,numdice +1):
                        roll=randrange(1,numsides,1)
                        print "Rolled %s %s-sided dice: %s" %(I,numsides,roll)
                        total=total+roll
                
                total+=modifier       
                print "Total rolled: %s (modifier %s)" % (total,modifier)
                print
                return total
                


def smart_input(message='',default=None,integer=False,decimal=False,validentries=[],indent=0,lower=False,upper=False,confirm=''):
    print
    error="no input"
    istr=""
    for I in range(0,indent):
        istr=" %s" %istr
    istr=''
    while error <> '':
        if error <> '' and error <> "no input":
            print "%s%s%s" %(istr,istr,error)
            print "\n\n"
        error=''
        printmessage=message
        printmessage="%s%s" %(istr,printmessage)
        if default:
            printmessage="%s (%s)" %(printmessage,default)
        if len(validentries) > 0:
            for entry in validentries:
                print "%s%s (%s): %s" %(istr,istr,validentries.index(entry)+1,entry)       
        print "%s ?" %printmessage,
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
                user_input =int(user_input)
            except Exception as E:
                error='Error:  %s' %E
        if decimal:
            try:
                user_input = float(user_input)
            except Exception as E:
                error='Error:  %s' %E
                
        else:
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
