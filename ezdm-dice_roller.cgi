#!/usr/bin/env python
from ezdm_libs.util import rolldice,smart_input,dice_list,highlight,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput

def main():
    highlight('EZDM - Dice Roller')
    numdice=smart_input('How many dice', integer=True,default=1)
    numsides=smart_input('What type',validentries=dice_list(),integer=True)
    modifier=smart_input('Modifier',integer=True,default=0)
    rolldice(True,numdice,numsides,modifier)

def getdata():
    formdic={}
    formdic["How many dice to roll"]='1'
    formdic["Type of dice to roll"]=dice_list()
    formdic["Modifier"]='0'
    formheader(border=3)
    dictinput(formdic)
    formfooter()

def webmain():
    cgiheader('EZDM - Dice Roller')
    data=parsecgi()
    if not 'submit' in data:
        getdata()
    else:
        rolldice(True,int(data["How many dice to roll"]),int(data["Type of dice to roll"]),int(data['Modifier']))
    cgifooter()

if __name__=='__main__': 
    if web:
        webmain()
    else:
        main()

