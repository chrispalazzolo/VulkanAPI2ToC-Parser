#!/usr/bin/python

import sys

pfile = sys.argv[1]
mfile = sys.argv[2]
efile = sys.argv[3]

print "File To Parse: {0}".format(pfile)
print "Save Methods To: {0}".format(mfile)
print "Save Enums To: {0}\n\n".format(efile)

# ========================================================================================================================

def ParseParams(params):
    params = params.strip()
    if params == "void":
        return ""
    params = params.replace(" **", "** ")
    params = params.replace(" *", "* ")
    params = params.replace(" params", " @params")
    params = params.replace(" ref", " @ref")
    params = params.replace(" base", " @base")
    return params

# ========================================================================================================================

if len(sys.argv) > 3 and pfile != "" and mfile != "" and efile != "":
    with open(pfile, "r") as infile, open(mfile, "w") as methodFile, open(efile, 'w') as enumFile:
        multiline = False
        currentLine = ""
        funcCt = 0
        defCt = 0
        comment = '';
        for line in infile:
            line = line.strip()
            line = ' '.join(line.split())
            line = line.replace("const ", "")
            if multiline:
                if line.find(";") > -1: # use find as the ; might be before comments
                    multiline = False
                    line = line.replace(");","")
                    end = ");\n"
                else:
                    multiline = True
                    end = ""
                params = ParseParams(line)
                line = " {0}{1}".format(params, end)
                currentLine = "{0}{1}".format(currentLine, line)
                if currentLine.find("*") > -1 and currentLine.find("unsafe") < 0:
                    currentLine = currentLine.replace("static extern", "static unsafe extern")
                if not multiline:
                    methodFile.write(currentLine)
                    currentLine = ""
            elif line.find("#define") == 0:
                if comment != "":
                    enumFile.write(comment)
                    comment = ""
                line = line.split(' ')
                if len(line) == 3:
                    defCt += 1
                    oname = line[1].split('_')
                    name = ''
                    for word in oname:
                        if word != "GL":
                            name += word.capitalize()
                
                    enumFile.write("{0} = UInt32({1})\n".format(name, line[2]))
            elif line.find('GLAPI') == 0:
                if line.find(';') > -1:
                    multiline = False
                    if comment != "":
                        methodFile.write(comment)
                        comment = ""
                else:
                    multiline = True

                line = line.replace("GLAPI ", "")
                line = line.replace("GLAPIENTRY ", "")
                line = line.replace("APIENTRY ", "")
                line = line.replace(" (", "(")
                fdec = line[0:line.index("(")]
                if fdec.find("*") > -1:
                    fdec = fdec.replace(fdec[0:fdec.index("*") + 1], "IntPtr")
                params = ParseParams(line[line.index("(") + 1: line.rindex(")") if not multiline else None])
                glFunc = fdec.split(' ')[-1]
                csFunc = glFunc.replace('gl', '')
                fdec = fdec.replace(glFunc, csFunc)
                endCap = ");\n" if not multiline else ""
                decl = "static extern" if params.find("*") < 0 else "static unsafe extern"
                currentLine = "{0} {1}({2}{3}".format(decl, fdec, params, endCap)
                methodFile.write('[DllImport(<<FILE>>, EntryPoint = "{0}", ExactSpelling = true)]\n'.format(glFunc))
                if not multiline:
                    methodFile.write(currentLine)
                    currentLine = ""
                funcCt += 1
            elif line.find("/*") == 0 or line.find('*') == 0 or line.find("*/") == 0:
                s = "{0}\n".format(line)
                comment = s if comment == '' else comment + s
else:
    print "Error: Arguments..."

print "Parse Complete!"
print "{0} possible define parsed.".format(defCt)
print "{0} function parsed.".format(funcCt)