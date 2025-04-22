#!/usr/bin/python

import sys

pfile = sys.argv[1] if len(sys.argv) > 1 else None

if pfile == "" or pfile == None:
    print "ABORTED: NO FILE"
    sys.exit(1)

spath = sys.argv[2] if len(sys.argv) > 2 else ""
if spath == "" or spath == None:
    spath = pfile[0:pfile.rfind('/')] if pfile.find('/') > -1 else ""
    print "\nWARNING: NO SAVE PATH, USING: {0}/".format(spath)
elif spath.endswith("/"):
    spath = spath[0:-1]

print "\nFile To Parse: {0}\n".format(pfile)
f = pfile[pfile.rfind("/"):].split(".")[0]
mfile = "{0}{1}_methods.cs".format(spath,f)
efile = "{0}{1}_enums.cs".format(spath,f)
sfile = "{0}{1}_structs.cs".format(spath,f)
cfile = "{0}{1}_consts.cs".format(spath,f)
dfile = "{0}{1}_delegates.cs".format(spath, f)
wfile = "{0}{1}_wrap_methods.cs".format(spath, f)

print "Saving Methods To: {0}".format(mfile)
print "Saving Enums To: {0}".format(efile)
print "Saving Structs To: {0}".format(sfile)
print "Saving Consts To: {0}".format(cfile)
print "Saving Delegates To: {0}".format(dfile)
print "Saving Wrapper Method To: {0}".format(wfile)

funcId = "VKAPI_ATTR"
funcPtr = "VKAPI_PTR"
funcJunk = "VKAPI_CALL "
structId = "typedef struct"
enumId = "typedef enum"
constId = "#define"
tab = "\t"
dtab = "\t\t"

def getEnumName(n, en):
    s = ''
    name = n.split('_')
    nam = ""
    for chunk in name:
        chunk = str.capitalize(chunk)
        s += chunk
        if en.find(s) == -1:
            nam += chunk
    return nam

def getConst(line):
    if line == None or line == "": return None
    line = line.split(" ")
    if len(line) < 3: return None
    slug = "int"
    if line[2].find('"') == 0:
        slug = "string"
    elif line[2] == "(~0U)":
        slug = "uint"
        line[2] = "~0"
    elif line[2] == "(~0ULL)":
        slug = "ulong"
        line[2] = "~0"
    elif line[2].endswith("f"):
        slug = "float"
        line[2] = line[2][:-1]
    return "const {0} {1} = {2};".format(slug, line[1], line[2])

def cToCSType(t, flag):
    if t.find("*") > -1:
        return "IntPtr"
    elif t == "VkFlags" or t == "VkBool32" or t == "VkSampleMask":
        return "UInt32"
    elif t == "VkDeviceSize":
        return "UInt64"
    else:
        if flag == "Vk":
            t = t.replace(flag, "")
        return t

def prepParamsAndArgs(paramLine, flag):
    params = []
    args = []
    paramLine = paramLine.split(',')
    for pair in paramLine:
        pair = pair.split(" ")
        pair[0] = cToCSType(pair[0], flag)
        params.append(" ".join(pair))
        if pair[0] == "IntPtr":
            pair[1] = "{0}.ToPointer()".format(pair[1])
        args.append(pair[1])
    return ", ".join(params), ", ".join(args)

def writeWrapperMethod(line, wfile):
    argPos = line.find("(")
    m = line[:argPos].split(" ")
    rtype = m[-2]
    if rtype.find("Vk") == 0:
        rtype = rtype.replace("Vk", "VK.")
    params, args = prepParamsAndArgs(line[argPos + 1: line.find(")")], "")
    csfunc = m[-1][2:]
    wfile.write("{0}public static ".format(dtab))
    if args.find("ToPointer") > -1:
        wfile.write("unsafe ")
    wfile.write("{0} {1}({2})\n".format(rtype, csfunc, params))
    wfile.write("\t\t{\n")
    wfile.write(tab)
    if rtype != "void":
        wfile.write("{0}return ".format(dtab))
    else:
        wfile.write(dtab)
    wfile.write("{0}({1});\n".format(m[-1], args))
    wfile.write("\t\t}\n\n")

def parseWriteMethodAndWrapper(line, mfile, wfile):
    rtxt = "static extern"
    
    if line.find("*") > -1:
        rtxt = rtxt + " unsafe"

    line = line.replace(funcId, rtxt)
    vfunc = line[line.rfind(funcJunk) + len(funcJunk): line.find("(")]
    line = line.replace(funcJunk, "")
    line = typeCleanUp(line)
    mfile.write('{0}[DllImport(<<FILE>>, EntryPoint = "{1}", ExactSpelling = true)]\n'.format(dtab, vfunc))
    mfile.write("{0}{1}\n".format(dtab, line))
    writeWrapperMethod(line, wfile)

#typedef VkResult (VKAPI_PTR *PFN_vkCreateInstance)(const VkInstanceCreateInfo* pCreateInfo, const VkAllocationCallbacks* pAllocator, VkInstance* pInstance);
def parseWriteDelegate(line, dfile):
    tmp = line.split(")(")
    func = tmp[0]
    params = tmp[1]
    func = func.replace("typedef ", "")
    func = func.replace("({0} *".format(funcPtr), "")
    tmp = func.split(" ")
    funcType = tmp[0]
    funcName = tmp[1]
    params = params.replace(");", "")
    if params != "void":
        params = typeCleanUp(params)
        params, args = prepParamsAndArgs(params, "Vk")
        params = params.replace("  ", " ")
    
    dfile.write("{0}public unsafe delegate {1} {2}({3});\n".format(dtab, funcType, funcName, params))
    dfile.write("{0}public static {1} {2};\n\n".format(dtab, funcName, funcName.replace("_vk", "")))

def typeCleanUp(line):
    line = line.replace('const ', "")
    line = line.replace("uint32_t", "UInt32")
    line = line.replace("int32_t", "Int32")
    line = line.replace("uint8_t", "byte")
    return line

def writeUsingAssignments(file):
    intPtr = "System.IntPtr"
    file.write("using VkInstance = {0};\n".format(intPtr))
    file.write("using VkPhysicalDevice = {0};\n".format(intPtr))
    file.write("using VkDevice = {0};\n".format(intPtr))
    file.write("using VkQueue = {0};\n".format(intPtr))
    file.write("using VkSemaphore = {0};\n".format(intPtr))
    file.write("using VkCommandBuffer = {0};\n".format(intPtr))
    file.write("using VkFence = {0};\n".format(intPtr))
    file.write("using VkDeviceMemory = {0};\n".format(intPtr))
    file.write("using VkBuffer = {0};\n".format(intPtr))
    file.write("using VkImage = {0};\n".format(intPtr))
    file.write("using VkEvent = {0};\n".format(intPtr))
    file.write("using VkQueryPool = {0};\n".format(intPtr))
    file.write("using VkBufferView = {0};\n".format(intPtr))
    file.write("using VkImageView = {0};\n".format(intPtr))
    file.write("using VkShaderModule = {0};\n".format(intPtr))
    file.write("using VkPipelineCache = {0};\n".format(intPtr))
    file.write("using VkPipelineLayout = {0};\n".format(intPtr))
    file.write("using VkRenderPass = {0};\n".format(intPtr))
    file.write("using VkPipeline = {0};\n".format(intPtr))
    file.write("using VkDescriptorSetLayout = {0};\n".format(intPtr))
    file.write("using VkSampler = {0};\n".format(intPtr))
    file.write("using VkDescriptorPool = {0};\n".format(intPtr))
    file.write("using VkDescriptorSet = {0};\n".format(intPtr))
    file.write("using VkFramebuffer = {0};\n".format(intPtr))
    file.write("using VkCommandPool = {0};\n".format(intPtr))

def writeFileHead(file, who):
    file.write("using System;\n")
    if who == "methods":
        file.write("using VkResult = System.Int32;\n")
    if who == "methods" or who == "wrapper":
        writeUsingAssignments(file)
    file.write("\nnamespace VK\n")
    file.write("{\n")
    if who == "wrapper" or who == "methods" or who == "const":
        file.write("\tpublic static partial class VK\n")
        file.write("\t{\n")

def writeClosing(file, who):
    if who == "wrapper" or who == "methods" or who == "const":
        file.write("\t}\n")
    file.write("}")

m_ct = 0
e_ct = 0
s_ct = 0
c_ct = 0
d_ct = 0

with open(pfile, "r") as infile, open(mfile, "w") as m_outfile, open(efile, 'w') as e_outfile, open(sfile, 'w') as s_outfile, open(cfile, 'w') as c_outfile, open(wfile, 'w') as w_outfile, open(dfile, 'w') as d_outfile:
    current = ""
    mline = ""
    dline = ""
    ename = ""
    
    writeFileHead(m_outfile, "methods")
    writeFileHead(w_outfile, "wrapper")
    writeFileHead(e_outfile, "enums")
    writeFileHead(c_outfile, "const")
    writeFileHead(s_outfile, "struct")
    writeFileHead(d_outfile, "delegates")

    for line in infile:
        line = line.strip()
        line = ' '.join(line.split())

        if current == "m":
            mline = mline + line
            if line.find(");") > -1:
                parseWriteMethodAndWrapper(mline, m_outfile, w_outfile)
                mline = ""
                current = ""

        elif current == "d":
            dline = dline + line
            if line.find(");") > -1:
                parseWriteDelegate(dline, d_outfile)
                dline = ""
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

        elif line.find(funcPtr) > 0:
            d_ct += 1
           
            if line.find(");") > -1:
                parseWriteDelegate(line, d_outfile)
                current = ""
                mline = ""
            else:
                current = "d"
                dline = line

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
    writeClosing(d_outfile, "delegates")

print "\nParse Completed!\n"
print "Found:"
print "Methods: {0}".format(m_ct)
print "Enums: {0}".format(e_ct)
print "Structs: {0}".format(s_ct)
print "Consts: {0}".format(c_ct)
print "Function Pointers: {0}\n".format(d_ct)