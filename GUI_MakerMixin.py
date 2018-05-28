#Gui_MakerMixin
from __future__ import print_function
import sys
#import Tkinter
from TkinterInterface import mFrame, mRootWindow, mGraphicsLibName, mPartial
import xml.etree.ElementTree as ET
# from functools import partial
from StringVarPlus import StringVarPlus
import copy


#Special Tags
PACK = 'pack'
VARIABLE = 'variable' # name="" typevar="" default="" onclick=""
FORM = 'form'
GROUP = 'group'
REPGROUP = 'repgroup' # tags="" data="" uniqueframe="false"
GRID = 'grid'
INCLUDE = 'include'
TEXTVARIABLE = 'textvariable'
FRAME = 'frame'

#Regular Tags that require special treatment
CHECKBUTTON = 'checkbutton'
RADIOBUTTON = 'radiobutton'
SCALE = 'scale'
BUTTON = 'button'
ENTRY = 'entry'

SPECIALTAGS = [CHECKBUTTON,RADIOBUTTON,SCALE,BUTTON,ENTRY,VARIABLE]

#Special Attributes
ONCLICK = 'onclick'
COMMAND = 'command'
TYPEVAR = 'typevar'
NAME = 'name'
GROUPLIST = 'grouplist'
DEFAULT = 'default'
VARNAME = 'varname'
VALUE = 'value'
TEXT = 'text'
FILENAME = 'filename'
TAGS = 'tags'
DATA = 'data'
UNIQUEFRAME = 'uniqueframe'

stack = []
stacklevel = 0

def pushFrame():
    global stacklevel
    stack.append(stacklevel)
    stacklevel += 1

def popFrame():
    global stacklevel
    val = stack.pop()
    stacklevel -= 1
    return val

#tags="abc:text,def:textvariable"
def extractRgAttribsDict(tags):
    """
    extract repgroup tags dict from tags attribute
    :param tags: str
    :return: dict
    """
    a1=tags.split(',')
    for n, s in enumerate(a1):
        a1[n]= s.strip()

    a2=[tuple(x.split(':')) for x in a1]
    opsdict = dict(a2)
    return opsdict

#data="tag:a,b,c,d|tag2:e,f,g,h"
def extractRgDataDict(data):
    """
    extract repgroup data from data attribute
    :param data: str
    :return: dict
    """
    b1 = data.split('|')
    for n, s in enumerate(b1):
        b1[n]= s.strip()

    b2 = [tuple(x.split(':')) for x in b1]
    datadict = dict(b2)
    for key in datadict:
        b3 = datadict[key].split(',')
        for n, s in enumerate(b3):
            b3[n] = s.strip()

        datadict[key] = b3

    return datadict



class GUI_MakerMixin(object):
    def __init__(self, topLevelWindow=None, outputfilename=None):
        if topLevelWindow is None:
            self.topLevelWindow = mRootWindow()
        else:
            self.topLevelWindow = topLevelWindow

        self.outputfp = sys.stdout
        if outputfilename is not None:
            #self.outputfp=sys.stdout
           self.outputfp = open(outputfilename,'w')

        self.emit("Hello World")

    def makeCommand(self, fnName, arg=None):
        """
        makeCommand takes fnName and turns it into an actual reference to the function
        :param fnName: str
        :param arg:
        :return: A reference to the actual function
        """
        if arg is None:
            if isinstance(fnName, str):
                return getattr(self, fnName)
            else:
                return fnName
        else:
            if isinstance(fnName, str):
                f = mPartial(getattr(self, fnName), arg)
                setattr(f,'__name__',fnName)
                return f
            else:
                f = mPartial(fnName, arg)
                setattr(f, '__name__', fnName)
                return f

    def xlateArgs(self,kwargs):
        for key in kwargs:
            if key != COMMAND and key != ONCLICK:
                try:
                    val = getattr(self, kwargs[key])
                    kwargs[key] = val
                except:
                    try:
                        val = getattr(mGraphicsLibName, kwargs[key])
                        kwargs[key] = val
                    except:
                        if '+' in kwargs[key]:
                            try:
                                tmp = kwargs[key].split('+')
                                val=""
                                for v in tmp:
                                    val += getattr(mGraphicsLibName, v)

                                kwargs[key] = val
                            except:
                                pass

                        else:
                            pass

        return kwargs

    def parseXMLFile(self, xmlfile):
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        return root

    def makeGUI(self, master, xmlfile):
        element = self.parseXMLFile(xmlfile)
        frame = self.processXmlElement(master, element)
        if element.tag == FORM:
            element.tag = 'Frame'

        #self.emitPackargs(element, '')

        if self.outputfp is not None and self.outputfp != sys.stdout:
            self.outputfp.close()

        return frame

    def extractAttrib(self, elem, attrib):
        """
            Extracts an attribute from an element and then removes it from the element.
            It returns the attribute value
        :type elem: ET.Element
        :type attrib: str
        : return attribute
        """
        val = elem.get(attrib)

        if val is not None:
            del(elem.attrib[attrib])
            return val

        raise Exception("%s not found in %s" % (attrib, elem.tag))

    def extractFunction(self, elem, attrib, run=True):
        """
        Extracts and returns a function reference from an element based on an attribute
        :param elem: ET.Element
        :param attrib: str
        :return: object
        """
        try:
            fnName = self.extractAttrib(elem, attrib)
            if fnName is not None:
                try:
                    func = getattr(self, fnName)
                except:
                    func = getattr(mGraphicsLibName, fnName)

                if run:
                    return func()
                else:
                    return func
        except:
            pass

        raise Exception("%s not found in %s" % (attrib,elem.tag))

    def extractPackargs(self, elem):
        packelem = elem.find(PACK)
        if packelem is not None:
            packargs = self.xlateArgs(packelem.attrib)
            elem.remove(packelem)
            return packargs

    def extractGridargs(self, elem):
        gridelem = elem.find(GRID)
        if gridelem is not None:
            gridargs = self.xlateArgs(gridelem.attrib)
            elem.remove(gridelem)
            return gridargs

    def emitPackargs(self,  widgetelem, packargs):
        pad = (stacklevel * '\t')
        print(pad + "{}.pack({})".format(widgetelem.tag, packargs))

    def emitGridargs(self, widgetelem, gridargs):
        pad = (stacklevel * '\t')
        print(pad + "{}.grid({})".format(widgetelem.tag, gridargs))

    def emitFrame(self,widgetname, master, *args, **kwargs):
        try:
            mastername = master.widgetName
        except:
            mastername = master.__class__.__name__

        pad = (stacklevel * '\t')
        #outputstr="{}({},{},{})".format(widgetname,mastername, args, kwargs)
        outputstr = "{}({}".format(widgetname, mastername)
        if len(args) > 0:
            outputstr += ", {}".format(args)

        if len(kwargs) > 0:
            outputstr += ", {}".format(str(kwargs)[1:-1].replace(': ','='))

        outputstr += ")"

        print(pad + outputstr,file=self.outputfp)

    def adjustWidgetArgs(self, args):
        args = args[0]

        if COMMAND in args:
            try:
                args[COMMAND] = args[COMMAND].func.__name__
            except:
                args[COMMAND] = args[COMMAND].__func__.__name__

        if VARIABLE in args:
            args[VARIABLE] = str(args[VARIABLE])

        if TEXTVARIABLE in args:
            args[TEXTVARIABLE] = str(args[TEXTVARIABLE])

        return args

    def emitWidget(self, widgetname, master, *args, **kwargs):
        try:
            mastername = master.widgetName
        except:
            mastername = master.__class__.__name__

        args = self.adjustWidgetArgs(args)
        if args is not None:
            outputstr = "{}({},{})".format(widgetname, mastername, args)
        else:
            outputstr="{}({})".format(widgetname,mastername)

        pad = (stacklevel * '\t')
        print(pad + outputstr,file=self.outputfp,**kwargs)

    def emit(self, *args, **kwargs):
        pad = (stacklevel * '\t')
        print(pad, *args, file=self.outputfp, **kwargs)

    def createFrame(self, master, *args, **kwargs):
        #str = (stacklevel * '\t') + "Frame"
        self.emitFrame("Frame",master, *args, **kwargs)
        pushFrame()
        return mFrame(master, *args, **kwargs)

    def createAttr(self, varname, varfunc):
        return setattr(self, varname, varfunc)

    def processSubelement(self, frame, subelement):
        packargs = self.extractPackargs(subelement)
        gridargs = None
        if packargs is None:
            gridargs = self.extractGridargs(subelement)

        widget = self.processXmlElement(frame, subelement)

        if subelement.tag == FORM or subelement.tag == INCLUDE or subelement.tag == REPGROUP:
            subelement.tag = FRAME.capitalize()

        if packargs is None and gridargs is None and widget is not None:
            self.emitPackargs(subelement, '')
            widget.pack()
        elif packargs is not None and widget is not None:
            self.emitPackargs(subelement, packargs)
            widget.pack(**packargs)
        elif gridargs is not None and widget is not None:
            self.emitGridargs(subelement, gridargs)
            widget.grid(**gridargs)



    def processForm(self, master, element):
        frameoptions = self.xlateArgs(element.attrib)
        frame = self.createFrame(master, **frameoptions)
        framepackargs = self.extractPackargs(element)

        framegridargs = None
        if framepackargs is None:
            framegridargs = self.extractGridargs(element)

        packargs = None

        for subelement in element:
            if subelement.tag != GROUP and subelement.tag != FORM:
                self.processSubelement(frame, subelement)
            else:
                widget = self.processXmlElement(frame, subelement)

        element.tag = 'Frame'
        popFrame()
        if framepackargs is None and framegridargs is None:
            #self.emit("frame.pack()")
            self.emitPackargs(element, '')
            frame.pack()
        elif framepackargs is not None:
            self.emitPackargs(element, packargs)
            frame.pack(**framepackargs)
        elif framegridargs is not None:
            self.emitGridargs(element, framegridargs)
            frame.grid(**framegridargs)


        return frame


    def processGroup(self, master, element):
        try:
            grpname = element.attrib[NAME]
            del (element.attrib[NAME])
        except:
            grpname = None

        try:
            grplistname = element.attrib[GROUPLIST]
            del (element.attrib[GROUPLIST])
        except:
            grplistname = None

        try:
            onclickfunc = self.extractAttrib(element, ONCLICK)
        except:
            onclickfunc = None

        try:
            varname = self.extractAttrib(element, VARNAME)
        except:
            varname = None

        try:
            varfunc = self.extractFunction(element, TYPEVAR)
        except:
            varfunc = None

        framepackargs = self.extractPackargs(element)

        framegridargs = None
        if framepackargs is None:
            framegridargs = self.extractGridargs(element)

        options = self.xlateArgs(element.attrib)
        frame = self.createFrame(master, **options)

        cblist = element.findall(CHECKBUTTON)
        if len(cblist) > 0:
            for cb in cblist:
                self.processSubelement(frame, cb)
                element.remove(cb)

            for subelement in element:
                self.processSubelement(frame, subelement)

        else:
            rblist = element.findall(RADIOBUTTON)
            if len(rblist) > 0:
                self.createAttr(varname, varfunc)

                for rb in rblist:
                    self.processSubelement(frame, rb)
                    element.remove(rb)

                for subelement in element:
                    self.processSubelement(frame, subelement)

            else:
                sslist = element.findall(SCALE)
                if len(sslist) > 0:
                    self.createAttr(varname, varfunc)

                    for ss in sslist:
                        self.processSubelement(frame, ss)
                        element.remove(ss)

                    for subelement in element:
                        self.processSubelement(frame, subelement)

                else:
                    for subelement in element:
                        self.processSubelement(frame, subelement)

        element.tag = 'Frame'
        popFrame()
        if framepackargs is None and framegridargs is None:
            self.emitPackargs(element, '')
            frame.pack()
        elif framepackargs is not None:
            self.emitPackargs(element, framepackargs)
            frame.pack(**framepackargs)
        elif framegridargs is not None:
            self.emitGridargs(element, framegridargs)
            frame.grid(**framegridargs)


        return frame

    def processEntryOptions(self, element, options):
        textvar = element.find(VARIABLE)
        if textvar is not None and NAME in textvar.attrib:
            varfunc = getattr(mGraphicsLibName, textvar.attrib[TYPEVAR])()
            varname = textvar.attrib[NAME]
            self.createAttr(varname, varfunc)
            options[TEXTVARIABLE] = varfunc
            element.remove(textvar)
            # index = element._children.index(textvar)
            # del(element._children[index])

        return options


    def processCheckbuttonOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            varfunc = getattr(mGraphicsLibName, optvar.attrib[TYPEVAR])()
            default = False
            if DEFAULT in optvar.attrib:
                default = optvar.attrib[DEFAULT]

            if default:
                varfunc.set(1)
            else:
                varfunc.set(0)

            if NAME in optvar.attrib:
                varname = optvar.attrib[NAME]
            elif TEXT in options:
                varname = "cb" + options[TEXT]
            else:
                raise Exception("Checkbutton Variable Tag missing name attribute")

            if ONCLICK in optvar.attrib:
                funcname = optvar.attrib[ONCLICK]
                options[COMMAND] = self.makeCommand(funcname, varname)

            self.createAttr(varname, varfunc)
            options[VARIABLE] = varfunc
            index = element._children.index(optvar)
            del (element._children[index])

        return options

    def processRadiobuttonOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            # varname = optvar.attrib[NAME]
            if NAME in optvar.attrib:
                varname = optvar.attrib[NAME]
            elif TEXT in options:
                varname = "rb" + options[TEXT]
            else:
                raise Exception("Radiobutton Variable Tag missing name attribute")
            # varfunc = getattr(self, varname)
            varfunc = self.extractFunction(optvar, NAME, run=False)

            default = False
            if DEFAULT in optvar.attrib:
                default = optvar.attrib[DEFAULT]

            if default:
                varfunc.set(1)
            else:
                varfunc.set(0)

            if ONCLICK in optvar.attrib:
                funcname = optvar.attrib[ONCLICK]
                options[COMMAND] = self.makeCommand(funcname, varname)

            options[VARIABLE] = varfunc
            element.remove(optvar)
            # index = element._children.index(optvar)
            # del (element._children[index])

        return options

    def processScaleOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            # varname = optvar.attrib[NAME]
            if NAME in optvar.attrib:
                varname = optvar.attrib[NAME]
            elif TEXT in options:
                varname = "ss" + options[TEXT]
            else:
                raise Exception("Scale Variable Tag missing name attribute")
            # varfunc = getattr(self, varname)
            varfunc = self.extractFunction(optvar, NAME, run=False)

            default = False
            if DEFAULT in optvar.attrib:
                default = optvar.attrib[DEFAULT]

            if default:
                varfunc.set(1)
            else:
                varfunc.set(0)

            if ONCLICK in optvar.attrib:
                funcname = optvar.attrib[ONCLICK]
                options[COMMAND] = self.makeCommand(funcname, varname)

            options[VARIABLE] = varfunc
            element.remove(optvar)
            # index = element._children.index(optvar)
            # del (element._children[index])

        return options

    def processIncludeTag(self, parent, elem):
        if FILENAME in elem.attrib:
            filename = elem.attrib[FILENAME]
            elem = self.parseXMLFile(filename)
            self.emitFrame(FRAME.capitalize(), parent)
            pushFrame()
            val = self.processXmlElement(parent, elem)
            popFrame()
            return val


    def processButtonOptions(self, element, options):
        if TEXT in options:
            btnName = options[TEXT]

            if COMMAND in options and isinstance(options[COMMAND], str):
                options[COMMAND] = self.makeCommand(options[COMMAND], btnName)

            elif ONCLICK in options:
                options[COMMAND] = self.makeCommand(options[ONCLICK], btnName)
                del (options[ONCLICK])

        return options


    def processVariableTagOptions(self, element, options):
        if NAME in options:
            varname = options[NAME]
            varfunc = options[TYPEVAR]()
            self.createAttr(varname, varfunc)
            if DEFAULT in options:
                default = options[DEFAULT]
                if default == 'true':
                    varfunc.set(1)
                else:
                    varfunc.set(0)
            # del(element)

        return options




    def processRepGroupTag(self, master, element):
        try:
            grpname = element.attrib[NAME]
            del (element.attrib[NAME])
        except:
            grpname = None

        try:
            grplistname = element.attrib[GROUPLIST]
            del (element.attrib[GROUPLIST])
        except:
            grplistname = None

        try:
            onclickfunc = self.extractAttrib(element, ONCLICK)
        except:
            onclickfunc = None

        try:
            varname = self.extractAttrib(element, VARNAME)
        except:
            varname = None

        try:
            varfunc = self.extractFunction(element, TYPEVAR)
        except:
            varfunc = None

        framepackargs = self.extractPackargs(element)

        framegridargs = None
        if framepackargs is None:
            framegridargs = self.extractGridargs(element)

        if TAGS in element.attrib:
            tags = element.get(TAGS)
            del(element.attrib[TAGS])
        else:
            tags = None

        if DATA in element.attrib:
            data = element.get(DATA)
            del(element.attrib[DATA])
        else:
            data = None

        if UNIQUEFRAME in element.attrib:
            uniqueframe = element.get(UNIQUEFRAME).lower() == "true"
            del(element.attrib[UNIQUEFRAME])
        else:
            uniqueframe = False

        if tags is not None and data is not None:
            rgAttribs = extractRgAttribsDict(tags)
            data = extractRgDataDict(data)
        else:
            raise Exception("repgroup tag missing tags and/or data atrributes")


        options = self.xlateArgs(element.attrib)
        # options = element.attrib

        frame = None
        if uniqueframe:
            self.emitFrame(FRAME.capitalize(), master)
            pushFrame()
            frame = self.createFrame(master, **options)

        numDataItems = len(data.values()[0])
        for n in range(numDataItems):
            if not uniqueframe:
                frame = self.createFrame(master, **options)

            for elem in element:
                subelem = copy.deepcopy(elem)
                try:
                    attribName = rgAttribs[subelem.tag]
                    subelem.attrib[attribName] = data[subelem.tag].pop(0)
                    if subelem.tag == ENTRY:
                        txtvar = subelem.find(VARIABLE)
                        if txtvar is not None:
                            txtvar.attrib[NAME] =  subelem.attrib[attribName]


                    widget = self.processSubelement(frame, subelem)

                except Exception as e:
                    print(e.message)

            if not uniqueframe:
                subelem.tag = FRAME.capitalize()
                popFrame()
                if framepackargs is None and framegridargs is None:
                    self.emitPackargs(subelem, '')
                    frame.pack()
                elif framepackargs is not None:
                    self.emitPackargs(subelem, copy.copy(framepackargs))
                    frame.pack(**framepackargs)
                elif framegridargs is not None:
                    self.emitPackargs(subelem, copy.copy(framegridargs))
                    frame.grid(**framegridargs)


        if uniqueframe:
            subelem.tag = FRAME.capitalize()
            popFrame()
            if framepackargs is None and framegridargs is None:
                self.emitPackargs(subelem, '')
                frame.pack()
            elif framepackargs is not None:
                self.emitPackargs(subelem, copy.copy(framepackargs))
                frame.pack(**framepackargs)
            elif framegridargs is not None:
                self.emitPackargs(subelem, copy.copy(framegridargs))
                frame.grid(**framegridargs)

            popFrame()
            return frame


    def processXmlElement(self, master, element):
        if element.tag == FORM:
            return self.processForm(master, element)

        elif element.tag == GROUP:
            return self.processGroup(master, element)

        elif element.tag == INCLUDE:
            return self.processIncludeTag(master, element)

        elif element.tag == REPGROUP:
            return self.processRepGroupTag(master, element)

        else:
            options = self.xlateArgs(element.attrib)
            packargs = None
            gridargs = None

            if len(element) or element.tag in SPECIALTAGS:
                if element.tag == BUTTON:
                    options = self.processButtonOptions(element, options)

                elif element.tag == ENTRY:
                    options = self.processEntryOptions(element, options)

                elif element.tag == CHECKBUTTON:
                    options = self.processCheckbuttonOptions(element, options)

                elif element.tag == RADIOBUTTON:
                    options = self.processRadiobuttonOptions(element, options)

                elif element.tag == SCALE:
                    options = self.processScaleOptions(element, options)

                elif element.tag == VARIABLE:
                    options = self.processVariableTagOptions(element, options)
                    return

                for subelement in element:
                    if subelement.tag == PACK:
                        packargs = self.extractPackargs(subelement)
                    elif subelement.tag == GRID:
                        gridargs = self.extractGridargs(subelement)
                    else:
                        options[subelement.tag] = subelement.text
                        if COMMAND in options and TEXT in options and isinstance(options[COMMAND], str):
                            options[COMMAND] = self.makeCommand(options[COMMAND], options[TEXT])

            widgetName = element.tag.capitalize()
            widget_factory = getattr(mGraphicsLibName, widgetName)


            if packargs is None and gridargs is None:
                self.emitWidget(widgetName, master, copy.copy(options))
                return widget_factory(master, **options)
            elif packargs is not None:
                self.emitWidget(widgetName, master, copy.copy(options), copy.copy(packargs))
                widget_factory(master, **options).pack(**packargs)
            elif gridargs is not None:
                self.emitWidget(widgetName, master, copy.copy(options), copy.copy(gridargs))
                widget_factory(master, **options).grid(**gridargs)




class TkGUI_MakerMixin(GUI_MakerMixin):
    def __init__(self, topLevelWindow=None, outputfilename=None):
        super(GUI_MakerMixin, self).__init__(topLevelWindow=topLevelWindow, outputfilename=outputfilename)

class Test(TkGUI_MakerMixin):
    def __init__(self, topLevelWindow=None, outputfilename=None):
        super(TkGUI_MakerMixin, self).__init__(topLevelWindow=topLevelWindow, outputfilename=outputfilename)

    def noop(self, *arg):
        """
        Sample onclick handler
        :param arg:
        :return:
        """
        if len(arg) == 1:
            if type(arg) == tuple:
                try:
                    myarg = getattr(self, arg[0])
                except:
                    myarg = arg[0]

                try:
                    if isinstance(myarg, StringVarPlus) or isinstance(myarg, mGraphicsLibName.IntVar):
                        # myarg = myarg.get()
                        print("noop called: %s:%s" % (arg[0],myarg.get()))
                        return
                except:
                    pass
            else:
                myarg = arg
        else:
            myarg = arg[0]
            print("noop called: %s:%s:%s" % (myarg, arg[1], getattr(self, myarg).get()))
            return
        print("noop called: %s" % myarg)


    def quit(self, *arg):
        """
        Sample onclick handler
        :param arg:
        :return:
        """
        exit()


    def fetch(self, arg):
        data={'Name':self.n1.get(),'Job':self.j1.get(), 'Pay':self.p1.get()}
        for label in data:
            value =data[label]
            print("%s:%s" % (label, value))

if __name__ == '__main__':
    root = mRootWindow()
    root.geometry("230x200")

    m1 = Test(root)
    fr = m1.makeGUI(root, "menu.xml")
    fr.pack()

    root.mainloop()
