#!/usr/bin/python

import sys
from HeaderFileParserBase import HeaderParserBase

class XLibParser(HeaderParserBase):
    m_ct = 0
    e_ct = 0
    s_ct = 0
    c_ct = 0
    
    def __init__(self, file, savePath):
        super(XLibParser, self).__init__(file, savePath)

    def parse(self):
        with open(self.inFile, "r") as infile, open(self.mSaveFile, "w") as m_outfile, open(self.eSaveFile, 'w') as e_outfile, open(self.sSaveFile, 'w') as s_outfile, open(self.cSaveFile, 'w') as c_outfile, open(self.wSaveFile, 'w') as w_outfile:
            current = ""
            mline = ""
            ename = ""
            comment = False
            
            writeFileHead(m_outfile, "methods")
            writeFileHead(w_outfile, "wrapper")
            writeFileHead(e_outfile, "enums")
            writeFileHead(c_outfile, "const")
            writeFileHead(s_outfile, "struct")

            for line in infile:
                line = line.strip()
                line = ' '.join(line.split())

                if line.find("/*") == 0:
                    comment = True
                    continue
                
                if line.find("*/") == 0:
                    comment = False
                    continue

                if comment == true:
                    continue
                
                if line.find("#define") == 0:
                    line = line.split(" ")
                    if len(line) > 2:
                        cType = "int"
                        if line[2].find('"') == 0:
                            slug = "string"
                        elif line[2].endswith("f"):
                            slug = "float"

                        cSaveFile.write("\n\t\tconst {0} {1} = {2}".format(slug, line[1], line[2]))
                        self.c_ct += 1
                
                


                if current == "m":
                    mline = mline + line
                    if line.find(");") > -1:
                        parseWriteMethodAndWrapper(mline, m_outfile, w_outfile)
                        mline = ""
                        current = ""

                elif line.find(constId) == 0:
                    l = getConst(line)

                    if l != None:
                        c_ct += 1
                        c_outfile.write("{0}{1}\n".format(dtab, l))

                elif line.find(enumId) == 0:
                    current = 'e'
                    e_ct += 1
                    ename = line[line.rfind("enum") + 5:line.find(" {")]
                    line = line.replace("typedef", "public")
                    line = line.replace(ename, ename[2:])
                    line = line.replace(" {", "")
                    e_outfile.write("{0}{1}\n".format(tab, line))
                    e_outfile.write("\t{\n")

                elif line.find(structId) == 0:
                    current = 's'
                    s_ct += 1
                    line = line.replace("typedef", "public")
                    line = line.replace(" {", "")
                    s_outfile.write("{0}{1}\n".format(tab, line))
                    s_outfile.write("\t{\n")

                elif line.find(funcId) == 0:
                    m_ct += 1
                    
                    if line.find(");") > -1:
                        parseWriteMethodAndWrapper(line, m_outfile, w_outfile)
                        current = ""
                        mline = ""
                    else:
                        current = "m"
                        mline = line

                elif current == "e":
                    if line.find("}") == 0 and line.endswith(";"):
                        e_outfile.write("\t};\n\n")
                        current = ""
                    else:
                        name = line[:line.find(" =")]
                        val = line[line.find("= ") + 2:]
                        nam = getEnumName(name, ename)
                        if val.find('_') > -1:
                            if val.find('+') > -1 or val.find('-') > -1:
                                minPos = val.find('-')
                                plusPos = val.find('+')
                                n1 = val[1:minPos - 1]
                                n2 = val[minPos + 2 : plusPos - 1]
                                val = val.replace(n1, getEnumName(n1, ename))
                                val = val.replace(n2, getEnumName(n2, ename))
                            else:
                                val = getEnumName(val, ename)
                        e_outfile.write("{0}{1} = {2}\n".format(dtab, nam, val))

                elif current == "s":
                    if line.find("}") == 0 and line.endswith(";"):
                        s_outfile.write("\t};\n\n")
                        current = ""
                    else:
                        line = line.replace("uint32_t", "UInt32")
                        line = line.replace("int32_t", "Int32")
                        line = line.replace("uint8_t", "byte")
                        s_outfile.write("{0}public {1}\n".format(dtab, line))

        writeClosing(m_outfile, "methods")
        writeClosing(w_outfile, "wrapper")
        writeClosing(e_outfile, "enum")
        writeClosing(c_outfile, "const")
        writeClosing(s_outfile, "struct")

        self.finishOutput()

    def writeHeader(self, fileToWrite, fileType):
        fileToWrite.write("using System;")
        fileToWrite.write("\n\nnamespace X11\n{")
        fileToWrite.write("\n\tpublic class XLib\n\t{\n")
    
    def writeClosing(self, fileToClose, fileType):
        fileToClose.write("\n\t\}\n}")
        
    def finishOutput(self):
        print "\nParse Completed!\n"
        print "Found:"
        print "Methods: {0}".format(self.m_ct)
        print "Enums: {0}".format(self.e_ct)
        print "Structs: {0}".format(self.s_ct)
        print "Consts: {0}\n".format(self.c_ct)