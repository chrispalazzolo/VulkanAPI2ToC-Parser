#!/usr/bin/python

import sys

class HeaderParserBase(object):
    inFile = ''
    savePath = ''

    cSaveFile = '' # file to save const to
    sSaveFile = '' # file to save structs to
    eSaveFile = '' # file to save enums to
    mSaveFile = '' # file to save methods to
    wSaveFile = '' # file to save wrapper methods to

    def __init__(self, inFile, savePath):
        if not self.checkFile(inFile):
            print "Error: No file provided, script aborted!"
            sys.exit()
        if not self.checkFile(savePath):
             savePath = inFile[0:inFile.rfind('/')] if inFile.find('/') > -1 else ""
             print "Warning: No save path provided. Using: {0}/".format(savePath)

        self.inFile = inFile
        self.savePath = savePath
        self.setSaveFiles()

    def checkFile(self, fileToCheck):
        if self.hasValue(fileToCheck):
            indx = fileToCheck.find(".")
            if indx > 0 and indx < len(fileToCheck) - 1:
                return True
        return False

    def checkPath(self, pathToCheck):
        return self.hasValue(pathToCheck)

    def hasValue(self, itemToCheck):
        if itemToCheck == "" or itemToCheck == None:
            return False
        else:
            return True

    def setSaveFiles(self):
        f = self.inFile[self.inFile.rfind('/'):].split(".")[0]

        self.mSaveFile = "{0}{1}_methods.cs".format(self.savePath,f)
        self.eSaveFile = "{0}{1}_enums.cs".format(self.savePath,f)
        self.sSaveFile = "{0}{1}_structs.cs".format(self.savePath,f)
        self.cSaveFile = "{0}{1}_consts.cs".format(self.savePath,f)
        self.wSaveFile = "{0}{1}_wrap_methods.cs".format(self.savePath, f)