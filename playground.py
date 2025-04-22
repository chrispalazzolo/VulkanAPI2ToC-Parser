#!/usr/bin/python

import numbers

str = "0x7FFFFFFF"

try:
    print int(str)
except:
    try:
        print float(str)
    except:
        print "Nope"