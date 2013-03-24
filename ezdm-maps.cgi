#!/usr/bin/env python
#First version limited automation
import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import clearscr,smart_input,load_json,json_from_template,highlight,say,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,template_conditional,validate_json
from ezdm_libs.util import cgihide as hide
from ezdm_libs.item import Item,list_items
from ezdm_libs import web,gui
