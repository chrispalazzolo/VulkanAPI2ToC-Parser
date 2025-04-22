#!/usr/bin/python

import sys
from XLibParser import XLibParser

from enum import Enum
class Parsers(Enum):
    xlib = 1
    x = 2
    vulkan = 3
    opengl = 4
    wayland = 5

    @classmethod
    def hasMember(self, nameToCheck):
        for name, member in self.__members__.items():
            if name == nameToCheck:
                return member
        return False

numOfArgs = len(sys.argv)
if numOfArgs < 2:
    print "Error: Missing argument(s). <which parser, file to parse, [path to save files]>"
    sys.exit(1)

inParser = sys.argv[1]
whichParse = Parsers.hasMember(inParser)

if not whichParse:
    print "Error: {0} is not a valid parser.".format(inParser)
    sys.exit(1)

pfile = sys.argv[2]
spath = sys.argv[3] if len(sys.argv) > 3 else None

if whichParse == Parsers.xlib:
    parser = XLibParser(pfile, spath)
    parser.parse()