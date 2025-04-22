#!/usr/bin/python

import sys

infile = sys.argv[1]

if infile == "" or infile == None:
    print "Error: No file."
    sys.exit(1)

print "Cleaning File: {0}".format(infile)

spath = infile[0:infile.rfind('/')] if infile.find('/') > -1 else ""
fname = infile[infile.rfind("/"):].split(".")[0]
sfile = spath + fname + "_clean.h"

print "Saving to: {0}".format(sfile)

with open(infile, "r") as f, open(sfile, "w") as outf:
    for l in f:
        num = l.split(" ")[0]
        l = l.replace(num, '')
        l = l.strip()
        outf.write(l + "\n")
    
print "Clean up Complete!"