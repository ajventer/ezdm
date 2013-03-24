#!/usr/bin/env python
#First version limited automation
import sys
import os
from simplejson import loads,dumps
from ezdm_libs import web,gui
from ezdm_libs.util import serve_image,parsecgi


if __name__ == "__main__":
    data=parsecgi()
    if 'icon' in data.keys():
        icon=data["icon"]
        serve_image(icon)
    else:
        print "Content-type: text/html"
        print "No image specified"

        
