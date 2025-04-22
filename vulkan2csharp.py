#!/usr/bin/python

import sys
import numbers
import decimal
import string

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
mfile = "{0}/VKLib.cs".format(spath)
efile = "{0}/Enums.cs".format(spath)
sfile = "{0}/Structs.cs".format(spath)
cfile = "{0}/Consts.cs".format(spath)
dfile = "{0}/FuncPtrs.cs".format(spath)
wfile = "{0}/Wrappers.cs".format(spath, f)
omitfile = "{0}/Omitted.txt".format(spath)

print "Saving Methods To: {0}".format(mfile)
print "Saving Enums To: {0}".format(efile)
print "Saving Structs To: {0}".format(sfile)
print "Saving Consts To: {0}".format(cfile)
print "Saving Delegates To: {0}".format(dfile)
print "Saving Wrapper Method To: {0}".format(wfile)

funcId = "VKAPI_ATTR"
funcPtrId = "VKAPI_PTR"
funcJunk = "VKAPI_CALL"
structId = "typedef struct"
unionId = "typedef union"
enumId = "typedef enum"
constId = "#define"

#Maps to hold newly parsed types
enumMap = {}
constMap = {}
structMap = {}
funcPtrMap = {}

#Map to hold counts of different items that were parsed
ctMap = {
    "methods": 0,
    "enums": 0,
    "structs": 0,
    "consts": 0,
    "funcPtrs": 0 
}

#Map to hold C/C++ types to C#
cToCSTypeMap = {
    "uint32_t": "uint",
    "int32_t": "int",
    "uint64_t": "ulong",
    "uint8_t" : "byte",
    "size_t": "ulong",
    "xcb_window_t": "UInt32",
    "HINSTANCE": "IntPtr",
    "HWND": "IntPtr",
    "Window": "ulong",
    "void": "void",
    "void*": "IntPtr",
    "char*": "string",
    "const": "readonly",
    "VkFlags": "uint",
    "VkBool32": "uint",
    "VkDeviceSize": "ulong",
    "VkSampleMask": "uint",
    "VkInstance": "IntPtr",
    "VkPhysicalDevice": "IntPtr",
    "VkDevice": "IntPtr",
    "VkQueue": "IntPtr",
    "VkSemaphore": "IntPtr",
    "VkCommandBuffer": "IntPtr",
    "VkFence": "IntPtr",
    "VkDeviceMemory": "IntPtr",
    "VkBuffer": "IntPtr",
    "VkImage": "IntPtr",
    "VkEvent": "IntPtr",
    "VkQueryPool": "IntPtr",
    "VkBufferView": "IntPtr",
    "VkImageView": "IntPtr",
    "VkShaderModule": "IntPtr",
    "VkPipelineCache": "IntPtr",
    "VkPipelineLayout": "IntPtr",
    "VkRenderPass": "IntPtr",
    "VkPipeline": "IntPtr",
    "VkDescriptorSetLayout": "IntPtr",
    "VkSampler": "IntPtr",
    "VkDescriptorPool": "IntPtr",
    "VkDescriptorSet": "IntPtr",
    "VkFramebuffer": "IntPtr",
    "VkCommandPool": "IntPtr",
    "VkSurfaceKHR": "IntPtr",
    "VkSwapchainKHR": "IntPtr",
    "VkDisplayKHR": "IntPtr",
    "VkDisplayModeKHR": "IntPtr",
    "VkDebugReportCallbackEXT": "IntPtr",
    "VisualID": "UInt64",
    "xcb_visualid_t": "UInt32"
}

typedefFlagsMap = {
    "VkInstanceCreateFlags": True,
    "VkFormatFeatureFlags": True,
    "VkImageUsageFlags": True,
    "VkImageCreateFlags": True,
    "VkSampleCountFlags": True,
    "VkQueueFlags": True,
    "VkMemoryPropertyFlags": True,
    "VkMemoryHeapFlags": True,
    "VkDeviceCreateFlags": True,
    "VkDeviceQueueCreateFlags": True,
    "VkPipelineStageFlags": True,
    "VkMemoryMapFlags": True,
    "VkImageAspectFlags": True,
    "VkSparseImageFormatFlags": True,
    "VkSparseMemoryBindFlags": True,
    "VkFenceCreateFlags": True,
    "VkSemaphoreCreateFlags": True,
    "VkEventCreateFlags": True,
    "VkQueryPoolCreateFlags": True,
    "VkQueryPipelineStatisticFlags": True,
    "VkQueryResultFlags": True,
    "VkBufferCreateFlags": True,
    "VkBufferUsageFlags": True,
    "VkBufferViewCreateFlags": True,
    "VkImageViewCreateFlags": True,
    "VkShaderModuleCreateFlags": True,
    "VkPipelineCacheCreateFlags": True,
    "VkPipelineCreateFlags": True,
    "VkPipelineShaderStageCreateFlags": True,
    "VkPipelineVertexInputStateCreateFlags": True,
    "VkPipelineInputAssemblyStateCreateFlags": True,
    "VkPipelineTessellationStateCreateFlags": True,
    "VkPipelineViewportStateCreateFlags": True,
    "VkPipelineRasterizationStateCreateFlags": True,
    "VkCullModeFlags": True,
    "VkPipelineMultisampleStateCreateFlags": True,
    "VkPipelineDepthStencilStateCreateFlags": True,
    "VkPipelineColorBlendStateCreateFlags": True,
    "VkColorComponentFlags": True,
    "VkPipelineDynamicStateCreateFlags": True,
    "VkPipelineLayoutCreateFlags": True,
    "VkShaderStageFlags": True,
    "VkSamplerCreateFlags": True,
    "VkDescriptorSetLayoutCreateFlags": True,
    "VkDescriptorPoolCreateFlags": True,
    "VkDescriptorPoolResetFlags": True,
    "VkFramebufferCreateFlags": True,
    "VkRenderPassCreateFlags": True,
    "VkAttachmentDescriptionFlags": True,
    "VkSubpassDescriptionFlags": True,
    "VkAccessFlags": True,
    "VkDependencyFlags": True,
    "VkCommandPoolCreateFlags": True,
    "VkCommandPoolResetFlags": True,
    "VkCommandBufferUsageFlags": True,
    "VkQueryControlFlags": True,
    "VkCommandBufferResetFlags": True,
    "VkStencilFaceFlags": True,
    "VkDebugReportFlagsEXT": True,
    "VkSurfaceTransformFlagsKHR": True,
    "VkSwapchainCreateFlagsKHR": True,
    "VkCompositeAlphaFlagsKHR": True,
    "VkDisplayPlaneAlphaFlagsKHR": True,
    "VkDisplayModeCreateFlagsKHR": True,
    "VkDisplaySurfaceCreateFlagsKHR": True,
    "VkXlibSurfaceCreateFlagsKHR": True,
    "VkXcbSurfaceCreateFlagsKHR": True,
    "VkWaylandSurfaceCreateFlagsKHR": True,
    "VkMirSurfaceCreateFlagsKHR": True,
    "VkAndroidSurfaceCreateFlagsKHR": True,
    "VkWin32SurfaceCreateFlagsKHR": True
}

reservedCSNameMap = {
    "object": "obj",
    "event": "evnt"
}

def getFlagCSharpType(flag):
    if typedefFlagsMap.get(flag, False):
        return cToCSTypeMap.get("VkFlags")
    return flag #return the flag so it errors in C# which then the type will need to manually figured out

def isVulkanType(vtype):
    if "*" in vtype: vtype = vtype.replace("*", "")
    if enumMap.get(vtype, False): return True
    if structMap.get(vtype, False): return True
    if constMap.get(vtype, False): return True
    if funcPtrMap.get(vtype, False): return True
    return False

def getCSType(cType):
    if "void*" in cType: return "IntPtr"
    if "char*" in cType: return "string"
    if "PFN_vk" in cType: return vkPFNNameToCSName(cType)

    isPtr = False
    csType = False
    if "*" in cType:
        isPtr = True
        cType = cType.replace("*", "")
    
    if "Flags" in cType:
        csType = getFlagCSharpType(cType)
    else:
        csType = cToCSTypeMap.get(cType, False)

    if csType != False:
        if isPtr and ("int" in csType or "long" in csType):
            csType = "ref {0}".format(csType)
        return csType

    if isPtr: return "IntPtr"

    if "Vk" in cType:
        cType = cType.replace("Vk", "")
        if isVulkanType(cType):
            return cType if not isPtr else "{0}*".format(cType) #return here because it can't have ref
    return cType

def cNumberSuffixesToCSharpType(val):
    val = str.upper(val)
    if "ULL" in val:
        return "UInt64"
    elif "LL" in val:
        return "Int64"
    elif "UL" in val:
        return "ulong"
    elif "L" in val:
        return "long"
    elif "U" in val:
        return "uint"
    return None

def cNumberSuffixValToCSharpVal(val):
    typeCast = cNumberSuffixesToCSharpType(val)
    if typeCast != None:
        val = str.upper(val)
        typeCast = "({0})".format(typeCast)
        if "(" in val: val = val[1:- 1]
        val = val.replace("U", "")
        val = val.replace("L", "")
        val = "{0}{1}".format(typeCast, val)
        if "~" in val:
            val = val.replace("~", "")
            val = "~{0}".format(val)
    return val
        
def guessCSharpTypeFromValue(val):
    if val == None or val == "": return None
    if val.endswith(";"):
        val = val.replace(";", "")
    if val.endswith(","):
        val = val.replace(",", "")
    if "ULL)" in val or "UL)" in val or "U)" in val: return cNumberSuffixesToCSharpType(val)
    if val.endswith('"'): return "string"
    if val.endswith("f") or "." in val: return "float"
    try:
        val = int(val)
        return "int"
    except:
        return val
    return val

def checkPropName(name):
    isPtr = False
    isArray = False
    if "*" in name:
        isPtr = True
        name = name.replace("*", "")
    if "[" in name:
        isArray = True
        name = name[0:name.find("[")]
    name = reservedCSNameMap.get(name, name)
    return name, isPtr, isArray
    

#pass the params as one string
def cToCSParamsAndArgs(params):
    if params == "void": return params, params
    rtrnParams = []
    rtrnArgs = []
    
    if "const" in params:
        params = params.replace("const ", "")
    
    params = params.split(",")
    
    for tv in params:
        tv = tv.strip()
        tv = tv.split(" ") #tv[0] = type, tv[1] = name
        if "*" in tv[1]:
            tv[1] = tv[1].replace("*", "")
            tv[0] = "{0}*".format(tv[0])
        csType = getCSType(tv[0])
        if tv[1] == "event":
            tv[1] = "evnt"
        elif tv[1] == "object":
            tv[1] = "obj"
        if "[" in tv[1]:
            csType = "{0}[]".format(csType)
            tv[1] = tv[1][0:tv[1].find("[")]
        rtrnParams.append("{0} {1}".format(csType, tv[1]))
        arg = tv[1]
        if(csType.find("ref") > -1):
            arg = "ref {0}".format(arg)
        rtrnArgs.append(arg)
    return ", ".join(rtrnParams), ", ".join(rtrnArgs)

def vkPFNNameToCSName(name):
    return name.replace("PFN_vk", "PFNvk")

def enumCPropNameToCSName(cName, enumName):
    cName = cName.replace("VK_", "")
    nameChunks = cName.split("_")
    cSharpName = ""
    testName = ""
    for nameChunk in nameChunks:
        nameChunk = str.capitalize(nameChunk)
        testName += nameChunk
        if testName not in enumName: #don't repeat enum name in enum properties
            cSharpName += nameChunk
    if cSharpName[0].isdigit():
        cSharpName = "Vk{0}".format(cSharpName)
    return cSharpName

def formatEnumPropsForCS(propsAndVals, enumName):
    cleanedPropsAndVals = []
    props = {}
    for pv in propsAndVals:
        pv = pv.split(" = ")
        pv[0] = enumCPropNameToCSName(pv[0], enumName)
        if "(" in pv[1]:
            vals = pv[1][1:pv[1].find(")")].replace(" + 1", "").split(" - ")
            vals[0] = enumCPropNameToCSName(vals[0], enumName)
            vals[1] = enumCPropNameToCSName(vals[1], enumName)
            pv[1] = "({0} - {1} + 1)".format(vals[0], vals[1])
        else:
            val = enumCPropNameToCSName(pv[1], enumName)
            if props.get(val, False):
                pv[1] = val
        cleanedPropsAndVals.append("{0} = {1}".format(pv[0], pv[1]))
        props[pv[0]] = "True"
    return cleanedPropsAndVals

def cleanAndPrepStructPropsForCS(props):
    returnProps = []
    for tp in props:
        tp = tp.replace(";", "")
        tp = tp.replace("const char* const*", "string")
        tp = tp.replace("const", "readonly")
        tp = tp.replace("struct ", "")
        tp = tp.split(" ")
        stype = tp[-2]
        isPtr = False
        isArray = False
        tp[-1], isPtr, isArray = checkPropName(tp[-1])
        if isPtr:
            tp[-2] = "IntPtr"
        else:
            if "*" in stype:
                if "char" in stype:
                    stype = "string"
                else:
                    stype = "IntPtr"
            elif stype.find("Flags") > -1:
                stype = getFlagCSharpType(stype)
            elif stype.find("Vk") == 0 and isVulkanType(stype.replace("Vk", "")):
                stype = stype.replace("Vk", "")
           
            else:
                stype = cToCSTypeMap.get(stype, stype)
                if "Vk" in stype: stype = stype.replace("Vk", "") # possible race condition as header files define types before use...
        
        if isArray:
            stype = "{0}[]".format(stype)

        tp[-2] = stype
        returnProps.append("{0};".format(" ".join(tp)))
    return returnProps

def parseAndWriteFunctionAndWrapper(line):
    line = line.replace("{0} ".format(funcId), "")
    line = line.replace("{0} ".format(funcJunk), "")
    funcTN = line[0:line.find("(")].split(" ")
    ftype = getCSType(funcTN[0])
    vkfname = funcTN[1]
    csfname = vkfname.replace("vk", "")
    params, args =  cToCSParamsAndArgs(line[line.find("(") + 1:line.find(")")])
    m_outfile.write('\t\t[DllImport(VK_OS_LIB_FILE, EntryPoint = "{0}", ExactSpelling = true, CallingConvention = CallingConvention.Winapi)]\n'.format(vkfname))
    m_outfile.write("\t\tstatic extern {0} {1}({2});\n\n".format(ftype, vkfname, params))
    w_outfile.write("\t\tpublic static {0} {1}({2}){3} {4}({5});{6}\n".format(ftype, csfname, params, "{" if ftype == "void" else " =>", vkfname, args, "}" if ftype == "void" else ""))
    ctMap["methods"] += 1

def parseAndWriteFunctionPtr(line):
    line = line.replace("typedef ", "")
    line = line.replace("{0} *".format(funcPtrId), "")
    parts = line.split("(")
    returnType = getCSType(prepLine(parts[0]))
    funcName = prepLine(parts[1])
    funcName = funcName.replace(")", "")
    cSharpName = vkPFNNameToCSName(funcName)
    params, args = cToCSParamsAndArgs(parts[2].replace(");", "")) #don't need the args here
    d_outfile.write("\t\t[UnmanagedFunctionPointer(CallingConvention.Winapi)]\n")
    d_outfile.write("\t\tpublic delegate {0} {1}({2});\n".format(returnType, funcName, params))
    d_outfile.write("\t\tpublic static {0} {1};\n\n".format(funcName, cSharpName))
    funcPtrMap[cSharpName] = True
    ctMap["funcPtrs"] += 1

def parseAndWriteStruct(line, isUnion):
    line = line.replace("{0} ".format(structId if not isUnion else unionId), "")
    name = line.split("{")[0].replace("Vk", "")
    structMap[name] = True
    props = cleanAndPrepStructPropsForCS(line[line.find("{") + 1:line.find(";}")].split(";"))
    if isUnion:
        s_outfile.write("\t\t[StructLayout(LayoutKind.Explicit)]\n")
    s_outfile.write("\t\tpublic struct {0}\n".format(name))
    s_outfile.write("\t\t{\n")
    for prop in props:
        if isUnion:
             s_outfile.write("\t\t\t[FieldOffset(0)]\n")
        s_outfile.write("\t\t\tpublic {0}\n".format(prop))
    s_outfile.write("\t\t};\n\n")
    ctMap["structs"] += 1

def parseAndWriteEnum(line):
    line = line.replace("{0} ".format(enumId), "")
    "".join(line.split()) # remove all spaces, tabs and newlines
    openCurlyBracePos = line.find("{")
    enumName = line[0:openCurlyBracePos -1].replace("Vk", "")
    enumMap[enumName] = True
    enumPropsAndVals = formatEnumPropsForCS(line[openCurlyBracePos + 1:line.find("}")].split(","), enumName)
    e_outfile.write("\t\tpublic enum {0}\n".format(enumName))
    e_outfile.write("\t\t{\n")
    e_outfile.write("\t\t\t{0}\n".format(",\n\t\t\t".join(enumPropsAndVals)))
    e_outfile.write("\t\t};\n\n")
    ctMap["enums"] += 1

def parseAndWriteConst(line):
    line = line.replace("{0} ".format(constId), "")
    nv = line.split(" ")
    if len(nv) < 3:
        nv[0] = nv[0].replace("VK_", "")
        constMap[nv[0]] = True
        constType = guessCSharpTypeFromValue(nv[1])
        if "U)" in nv[1] or "L)" in nv[1]:
            nv[1] = cNumberSuffixValToCSharpVal(nv[1])
        if constType != nv[1]:
            c_outfile.write("\t\tconst {0} {1} = {2};\n".format(constType, nv[0], nv[1]))
            ctMap["consts"] += 1

def parseLine(line):
    if funcId in line:
        parseAndWriteFunctionAndWrapper(line)
    elif funcPtrId in line:
        parseAndWriteFunctionPtr(line)
    elif line.find(structId) == 0: #checking if at start of line... ignores stucts in #define
        parseAndWriteStruct(line, False)
    elif unionId in line:
        parseAndWriteStruct(line, True)
    elif enumId in line:
        parseAndWriteEnum(line)
    elif constId in line:
        parseAndWriteConst(line)
    else:
        if line != "" and line != None and line != " ":
            omit_file.write("{0} //====== line ignored\n".format(line))

def prepLine(line):
    line = line.strip()
    line = ' '.join(line.split())
    return line

def writeCSharpFileHeading(ofile):
    ofile.write("using System;\n")
    ofile.write("using System.Runtime.InteropServices;\n")
    ofile.write("using System.Text;\n\n")
    ofile.write("namespace VulkanDotNet\n")
    ofile.write("{\n")
    ofile.write("\tpublic partial class Vk\n")
    ofile.write("\t{\n")

def writeCSharpFileFooting(ofile):
    ofile.write("\t}\n")
    ofile.write("}")

def writeToAllFiles(writeWhat):
    if writeWhat == "heading":
        writeCSharpFileHeading(m_outfile)
        writeCSharpFileHeading(w_outfile)
        writeCSharpFileHeading(e_outfile)
        writeCSharpFileHeading(c_outfile)
        writeCSharpFileHeading(s_outfile)
        writeCSharpFileHeading(d_outfile)
    elif writeWhat == "footing":
        writeCSharpFileFooting(m_outfile)
        writeCSharpFileFooting(w_outfile)
        writeCSharpFileFooting(e_outfile)
        writeCSharpFileFooting(c_outfile)
        writeCSharpFileFooting(s_outfile)
        writeCSharpFileFooting(d_outfile)

def writeOSLibFile(ofile):
    prop = "\t\tprivate const string VK_OS_LIB_FILE = "
    ofile.write("#if WINDOWS\n")
    ofile.write("{0}\"vulkan-1.dll\";\n".format(prop))
    ofile.write("#elif OSX\n")
    ofile.write("{0}\"libvulkan.so\";\n".format(prop))
    ofile.write("#elif LINUX\n")
    ofile.write("{0}\"libvulkan.so\";\n".format(prop))
    ofile.write("#endif\n\n")

with open(pfile, "r") as infile, open(mfile, "w") as m_outfile, open(efile, 'w') as e_outfile, open(sfile, 'w') as s_outfile, open(cfile, 'w') as c_outfile, open(wfile, 'w') as w_outfile, open(dfile, 'w') as d_outfile, open(omitfile, 'w') as omit_file:
    writeToAllFiles("heading")
    writeOSLibFile(m_outfile)

    isMultiLine = False
    buildLine = ""

    for line in infile:
        line = prepLine(line)

        if isMultiLine == True:
            buildLine += line
            if "}" in line or line.endswith(");"):
                buildLine = prepLine(buildLine)
                isMultiLine = False
                line = buildLine
                buildLine = ""
            else:
                continue
        elif line.endswith('{') or line.endswith('('):
            isMultiLine = True
            buildLine = line
            continue

        parseLine(line)
    
    writeToAllFiles("footing")

print "\nParse Completed!\n"
print "Found:"
print "Methods: {0}".format(ctMap["methods"])
print "Enums: {0}".format(ctMap["enums"])
print "Structs: {0}".format(ctMap["structs"])
print "Consts: {0}".format(ctMap["consts"])
print "Function Pointers: {0}\n".format(ctMap["funcPtrs"])