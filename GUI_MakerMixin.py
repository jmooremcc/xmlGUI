#Gui_MakerMixin
#
#       Copyright (C) 2018
#       John Moore (jmooremcc@hotmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
#
from __future__ import print_function
import sys
import copy
import re
#import Tkinter
try:
    from Tkinter import *
    import Tkconstants
except ImportError:
    from tkinter import *
    from tkinter import ttk
    import tkinter.constants
    import tkinter as tk
    Tkconstants = tkinter.constants

from TkinterInterface import mFrame, mRootWindow, mGraphicsLibName, mPartial, mttkGraphicsLibName
import xml.etree.ElementTree as ET
# from functools import partial
from StringVarPlus import StringVarPlus
from utilities import GetAttr, createIcon, createPhotoImage



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
IMAGE = 'image'
PLACE = 'place'
PHOTOIMAGE = 'photoimage'
ROTATION = 'rotation'
CONFIGURE = 'configure'
OBJ = 'obj'
EXPR ='expr'
COLUMN = 'column'
ROW = 'row'
CHOICES = 'choices'
SEPARATOR = 'separator'
BIND = 'bind'
PARAMS = 'params'
SRCHEXP = '__param__.*'

#Regular Tags that require special treatment
CHECKBUTTON = 'checkbutton'
RADIOBUTTON = 'radiobutton'
SCALE = 'scale'
BUTTON = 'button'
ENTRY = 'entry'
LABEL = 'label'
OPTIONMENU = 'optionmenu'

SPECIALTAGS = [CHECKBUTTON,RADIOBUTTON,SCALE,BUTTON,ENTRY,VARIABLE,TEXTVARIABLE,LABEL, CONFIGURE, OPTIONMENU, BIND]

#Special Attributes
ONCLICK = 'onclick'
COMMAND = 'command'
TYPEVAR = 'typevar'
NAME = 'name'
GROUPLIST = 'grouplist'
DEFAULT = 'default'
VARNAME = 'varname'
VARNAMES = 'varnames'
VALUE = 'value'
TEXT = 'text'
FILENAME = 'filename'
TAGS = 'tags'
DATA = 'data'
UNIQUEFRAME = 'uniqueframe'
NOARG = 'noarg'
SIZE = 'size'
ONCHANGE = 'onchange'
stack = []
stacklevel = 0
outputfp = sys.stdout

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

def extractParms(elem):
    parms={}

    for e in elem.findall(PARAMS): #type: ET
        parms.update(e.attrib)

    return parms if len(parms) > 0 else None

def processParms(elem, parms):
    if elem.text is not None:
        m=re.match(SRCHEXP, elem.text)
        if m is not None:
            elem.text = parms[m.string]

    for k,v in elem.attrib.items():
        m=re.match(SRCHEXP,v)
        if m is not None:
            try:
                value = parms[m.string]
                elem.attrib[k] = value
            except Exception as e:
                raise Exception(f"ERROR: Invalid Parm -> {k}:{m.string} in element {elem.tag}")

    for e in elem:
        processParms(e, parms)


def GetAttr(parent, fnname):
    nlist = [parent] + fnname.split('.')
    numitems = len(nlist)
    if numitems > 2:
        for n in range(numitems - 1):
            nlist[n + 1] = GetAttr(nlist[n], nlist[n + 1])

        return nlist[numitems - 1]
    else:
        return getattr(parent, fnname)

def xlateArgs(obj,kwargs):
    for key in kwargs:
        if key != COMMAND and key != ONCLICK:
            try:
                val = GetAttr(obj, kwargs[key])
                kwargs[key] = val
            except:
                try:
                    val = GetAttr(mGraphicsLibName, kwargs[key])
                    kwargs[key] = val
                except:
                    if '+' in kwargs[key]:
                        try:
                            tmp = kwargs[key].split('+')
                            val=""
                            for v in tmp:
                                val += GetAttr(mGraphicsLibName, v)

                            kwargs[key] = val
                        except:
                            pass

                    else:
                        pass

    return kwargs

def extractPackargs(obj, elem):
    packelem = elem.find(PACK)
    if packelem is not None:
        packargs = xlateArgs(obj, packelem.attrib)
        elem.remove(packelem)
        return packargs

def extractGridargs(obj, elem):
    gridelem = elem.find(GRID)
    if gridelem is not None:
        gridargs = xlateArgs(obj, gridelem.attrib)
        elem.remove(gridelem)
        return gridargs

def extractPlaceargs(obj, elem):
    placeelem = elem.find(PLACE)
    if placeelem is not None:
        placeargs = xlateArgs(obj, placeelem.attrib)
        elem.remove(placeelem)
        return placeargs

def emitPackargs(widgetelem, packargs):
    pad = (stacklevel * '\t')
    print(pad + "{}.pack({})".format(widgetelem.tag, packargs))

def emitGridargs(widgetelem, gridargs):
    pad = (stacklevel * '\t')
    print(pad + "{}.grid({})".format(widgetelem.tag, gridargs))

def emitPlaceargs(widgetelem, placeargs):
    pad = (stacklevel * '\t')
    print(pad + "{}.placeargs({})".format(widgetelem.tag, placeargs))

def adjustWidgetArgs(args):
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

def emitWidget(widgetname, master, *args, **kwargs):
    try:
        mastername = master.widgetName
    except:
        mastername = master.__class__.__name__

    args = adjustWidgetArgs(args)
    if args is not None:
        outputstr = "{}({},{})".format(widgetname, mastername, args)
    else:
        outputstr="{}({})".format(widgetname,mastername)

    pad = (stacklevel * '\t')
    print(pad + outputstr,file=outputfp ,**kwargs)

def emit(*args, **kwargs):
    pad = (stacklevel * '\t')
    print(pad, *args, file=outputfp , **kwargs)

def emitFrame(widgetname, master, *args, **kwargs):
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

    print(pad + outputstr,file= outputfp)


class CreateGUI_Window():
    def __init__(self, apptitle, windowsize=(600,400)):
        root = self.root = tk.Tk()
        self.toplevel = self.root.winfo_toplevel()
        self.root.title(apptitle)
        self.root.minsize(*windowsize)
        self.root.resizable(0, 0)
        self.root.protocol('WM_DELETE_WINDOW', self.onExit)  # root is your root window
        frame = tk.Frame(root, bd=2)
        frame.pack(side=TOP, fill=BOTH)
        return frame

    def onExit(self):
        exit()

class LayoutManager():
    def __init__(self, element, parent = None, elementName=None):
        self.element = element
        self.gridargs = None
        self.placeargs = None
        self.packargs = None
        self.elementName = elementName
        self.parent = parent

        if element is None:
            return

        self.packargs = extractPackargs(self, element)

        if self.packargs is None:
            self.gridargs = extractGridargs(self, element)

        if self.gridargs is None and self.packargs is None:
            self.placeargs = extractPlaceargs(self, element)


    def applyLayoutToWidget(self, widget):
        if self.element is None:
            emit(FRAME.capitalize(), '')
            widget.pack()
            return

        if self.element.tag == FORM or self.element.tag == INCLUDE or self.element.tag == REPGROUP:
            self.element.tag = self.elementName

        if self.packargs is None and self.gridargs is None and self.placeargs is None and widget is None:
            emitPackargs(self.element, '')
            widget.pack()
        elif self.packargs is None and self.gridargs is None and self.placeargs is None and widget is not None:
            if self.elementName is None:
                emit(FRAME.capitalize())
            else:
                self.element.tag = self.element.tag.capitalize()
                emitPackargs(self.element, '')

            widget.pack()
        elif self.packargs is not None and widget is not None:
            propagateflag = False
            if 'propagate' in self.packargs.keys():
                propagateflag = True
                propagateValue = self.packargs['propagate']
            emitPackargs(self.element, self.packargs)
            if propagateflag:
                widget.pack_propagate(propagateValue)
                del self.packargs['propagate']

            widget.pack(**self.packargs)

        elif self.gridargs is not None and widget is not None:
            emitGridargs(self.element, self.gridargs)
            widget.grid(**self.gridargs)
        elif self.placeargs is not None and widget is not None:
            emitPlaceargs(self.element, self.placeargs)
            widget.place(**self.placeargs)


class GenerateFrame():
    def __init__(self, parent, element=None, frametype=PACK, frameargs={}, **framekwargs):
        self.parent = parent
        self.frametype = frametype
        self.elementName = FRAME.capitalize()

        if element is None:
            options = xlateArgs(self, framekwargs)
        else:
            self.elementName = "{}{}".format(element.tag.capitalize(), FRAME.capitalize())
            self.processElement(element)
            self.options = options = xlateArgs(self, element.attrib)

        self.frame = Frame(parent, **options)
        emitFrame(self.elementName, parent, **options)
        pushFrame()


    @property
    def Frame(self):
        return self.frame

    def clone(self):
        newfr = copy.copy(self)
        newfr.frame = Frame(self.frame, **self.options)
        emitFrame(self.elementName, self.parent, **self.options)
        pushFrame()
        return newfr

    def layoutFrame(self, **kwargs):
        popFrame()
        self.layout.applyLayoutToWidget(self.frame)

    def processElement(self, element):
        self.layout = LayoutManager(element, parent=self.parent, elementName=self.elementName)



class GUI_MakerMixin(object):
    def __init__(self, topLevelWindow=None, outputfilename=None):
        global outputfp

        if topLevelWindow is None:
            self.topLevelWindow = mRootWindow()
        else:
            self.topLevelWindow = topLevelWindow

        outputfp = sys.stdout
        if outputfilename is not None:
            #outputfp =sys.stdout
           outputfp = open(outputfilename,'w')

        # self.emit("Hello World")


    def makeCommand(self, fnName, arg=None):
        """
        makeCommand takes fnName and turns it into an actual reference to the function
        :param fnName: str
        :param arg:
        :return: A reference to the actual function
        """
        if arg is None:
            if isinstance(fnName, str):
                return GetAttr(self, fnName)
            else:
                return fnName
        else:
            if isinstance(fnName, str):
                f = mPartial(GetAttr(self, fnName), arg)
                setattr(f,'__name__',fnName)
                return f
            else:
                f = mPartial(fnName, arg)
                setattr(f, '__name__', fnName)
                return f


    def parseXMLFile(self, xmlfile):
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        return root

    def makeGUI(self, master, xmlfile):
        element = self.parseXMLFile(xmlfile)
        self.processXmlElement(master, element)

        if outputfp is not None and outputfp != sys.stdout:
            outputfp .close()


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
                    func = GetAttr(self, fnName)
                except:
                    func = GetAttr(mGraphicsLibName, fnName)

                if run:
                    return func()
                else:
                    return func
        except:
            pass

        raise Exception("%s not found in %s" % (attrib,elem.tag))


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

        print(pad + outputstr,file=outputfp )


    def createFrame(self, master, *args, **kwargs):
        #str = (stacklevel * '\t') + "Frame"
        emitFrame(FRAME.capitalize(),master, *args, **kwargs)
        pushFrame()
        return mFrame(master, *args, **kwargs)

    def createAttr(self, varname, varfunc):
        return setattr(self, varname, varfunc)

    def processSubelement(self, frame, subelement):
        widget = self.processXmlElement(frame, subelement)
        return widget


    def processForm(self, master, element):
        fr = GenerateFrame(master, element)
        widget = None

        for subelement in element:
            if subelement.tag != GROUP and subelement.tag != FORM:
                self.processSubelement(fr.Frame, subelement)
            else:
                widget = self.processXmlElement(fr.Frame, subelement)

        fr.layoutFrame()
        if widget is not None:
            return widget


    def processGroup(self, master, element):
        try:
            grplistname = element.attrib[GROUPLIST]
            del (element.attrib[GROUPLIST])
        except:
            grplistname = None

        try:
            grpname = element.attrib[NAME]
            del (element.attrib[NAME])
        except:
            grpname = None


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

        fr = GenerateFrame(master, element)

        cblist = element.findall(CHECKBUTTON)
        if len(cblist) > 0:
            for cb in cblist:
                self.processSubelement(fr.Frame, cb)
                element.remove(cb)

            for subelement in element:
                self.processSubelement(fr.Frame, subelement)

        else:
            rblist = element.findall(RADIOBUTTON)
            if len(rblist) > 0:
                self.createAttr(varname, varfunc)

                for rb in rblist:
                    self.processSubelement(fr.Frame, rb)
                    element.remove(rb)

                for subelement in element:
                    self.processSubelement(fr.Frame, subelement)

            else:
                sslist = element.findall(SCALE)
                if len(sslist) > 0:
                    self.createAttr(varname, varfunc)

                    for ss in sslist:
                        self.processSubelement(fr.Frame, ss)
                        element.remove(ss)

                    for subelement in element:
                        self.processSubelement(fr.Frame, subelement)

                else:
                    for subelement in element:
                        self.processSubelement(fr.Frame, subelement)

        fr.layoutFrame()

    def processEntryOptions(self, element, options):
        textvar = element.find(VARIABLE)
        if textvar is None:
            textvar = element.find(TEXTVARIABLE)

        if textvar is not None and NAME in textvar.attrib:
            varfunc = GetAttr(mGraphicsLibName, textvar.attrib[TYPEVAR])()
            varname = textvar.attrib[NAME]
            self.createAttr(varname, varfunc)
            options[TEXTVARIABLE] = varfunc

            if VALUE in textvar.attrib:
                value = textvar.attrib[VALUE]
                varfunc.set(value)
                del textvar.attrib[VALUE]

            element.remove(textvar)

        if element.tag == LABEL:
            lblname = None
            if NAME in options:
                lblname = options[NAME]
                del options[NAME]
            if PHOTOIMAGE in options:
                imageFile = options[PHOTOIMAGE]
                rotation = 0
                if ROTATION in options:
                    rotation = int(options[ROTATION])
                    del options[ROTATION]
                photoimage = createPhotoImage(imageFile, defaultimage=r"TV.jpg", angle=rotation)
                options[IMAGE] = photoimage
                del options[PHOTOIMAGE]
                if lblname is not None:
                    self.createAttr(lblname + "PhotoImage", photoimage)


        return options


    def processCheckbuttonOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            varfunc = GetAttr(mGraphicsLibName, optvar.attrib[TYPEVAR])()
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
                options[COMMAND] = self.makeCommand(funcname, self.processNoArg(optvar.attrib, varname))

            self.createAttr(varname, varfunc)
            options[VARIABLE] = varfunc
            try:
                element.remove(optvar)
            except: pass

        return options

    def processMenuoptionOptions(self, element, options):
        args = None
        optvar = element.find(TEXTVARIABLE)
        if optvar is None:
            optvar = element.find(VARIABLE)

        if optvar is not None:
            if NAME in optvar.attrib:
                varname = optvar.attrib[NAME]
            else:
                raise Exception("OptionMenu Variable Tag missing name attribute")

            varfunc = GetAttr(mGraphicsLibName, optvar.attrib[TYPEVAR])() #type StringVar
            self.createAttr(varname, varfunc)
            try:
                element.remove(optvar)
            except:
                pass

            try:
                onChangefunc = options[ONCHANGE]
                del options[ONCHANGE]
                cb = lambda name, index, mode, var=varfunc : onChangefunc(var)
                varfunc.trace('w', cb)
            except: pass

        if CHOICES in options:
            try:
                choicelist = options[CHOICES].split(',') #type:list
                choicelist = [choice.strip() for choice in choicelist]
                del options[CHOICES]
                value = choicelist[0]

                if varfunc is not None:
                    varfunc.set(value)

                choicelist.insert(0, varfunc)
                args = choicelist
            except:
                varname = options[CHOICES]
                del options[CHOICES]
                choicelist = varname.get().split(',')
                choicelist = [choice.strip() for choice in choicelist]
                varname.set(choicelist[0])
                choicelist.insert(0,varname)
                args = choicelist

        return args


    def processRadiobuttonOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            if NAME in optvar.attrib:
                varname = optvar.attrib[NAME]
            elif TEXT in options:
                varname = "rb" + options[TEXT]
            else:
                raise Exception("Radiobutton Variable Tag missing name attribute")

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
                options[COMMAND] = self.makeCommand(funcname, self.processNoArg(optvar.attrib, varname))

            options[VARIABLE] = varfunc
            element.remove(optvar)

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
            # varfunc = GetAttr(self, varname)
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
                options[COMMAND] = self.makeCommand(funcname, self.processNoArg(optvar.attrib, varname))

            options[VARIABLE] = varfunc
            element.remove(optvar)
            # index = element._children.index(optvar)
            # del (element._children[index])

        return options

    def processBindOptions(self, element, options:dict):
        try:
            widget = options['obj'] #type:tk.Widget
            var = options['var']
            callback = options['callback']
            events = [ f"<{event.strip()}>" for event in options['events'].split(',')]

            cb = lambda e, arg=var: callback(e, arg)
            for event in events:
                widget.bind(event, cb)

        except Exception as e:
            print(f"Bind Error:\n\t{str(e)}")





    def processIncludeTag(self, parent, elem):

        parms = extractParms(elem)

        if FILENAME in elem.attrib:
            filename = elem.attrib[FILENAME]
            elem = self.parseXMLFile(filename)
            # if parms is not None:
            processParms(elem, parms)

            val = self.processXmlElement(parent, elem)

            return val

    def processNoArg(self, options, var):
        noarg = False
        if NOARG in options:
            if options[NOARG].lower() == 'true':
                noarg = True

            del options[NOARG]

        if noarg:
            return None
        else:
            return var


    def processButtonOptions(self, element, options):
        btnName = None
        icon = None
        isize = (32,32)

        if TEXT in options:
            btnName = options[TEXT]
            del options[TEXT]

        if NAME in options:
            btnName = options[NAME]
            # del options[NAME]

        if SIZE in options:
            isize = tuple(map(int,options[SIZE].split(',')))
            del options[SIZE]

        try:
            imageFile = options[IMAGE]
            icon = createIcon(imageFile, size=isize)
            # self.tmpicon = createPhotoImage(imageFile, size=isize)
            options[IMAGE] = icon
        except Exception as e:
            pass

        if btnName is not None:
            if COMMAND in options and isinstance(options[COMMAND], str):
                options[COMMAND] = self.makeCommand(options[COMMAND], self.processNoArg(options, btnName))

            elif ONCLICK in options:
                options[COMMAND] = self.makeCommand(options[ONCLICK], self.processNoArg(options, btnName))
                del (options[ONCLICK])
        elif len(options) > 0:
            tmp = element.find(TEXT)
            if tmp is not None:
                btnName = tmp.text

                if COMMAND in options:
                    options[COMMAND] = self.makeCommand(options[COMMAND], self.processNoArg(options, btnName))
                elif ONCLICK in options:
                    options[COMMAND] = self.makeCommand(options[ONCLICK], self.processNoArg(options, btnName))
                    del (options[ONCLICK])


        if icon is not None:
            self.createAttr(btnName + "Icon", icon)


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

        if VARNAMES in element.attrib:
            varnames = element.get(VARNAMES)
            del (element.attrib[VARNAMES])
        else:
            varnames = None

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

        if varnames is not None:
            varnames = extractRgAttribsDict(varnames)

        mstrfr = GenerateFrame(master, element)

        numDataItems = len(list(data.values())[0])
        for n in range(numDataItems):
            if not uniqueframe:
                # frame = self.createFrame(master, **options)
                fr = mstrfr.clone()
            for elem in element:
                subelem = copy.deepcopy(elem)
                try:
                    attribName = rgAttribs[subelem.tag]
                    subelem.attrib[attribName] = data[subelem.tag].pop(0)
                    gridelem = subelem.find(GRID)
                    if gridelem is not None:
                        if COLUMN in gridelem.attrib:
                            gridelem.attrib[ROW] = str(n)
                        elif ROW in gridelem.attrib:
                            gridelem.attrib[COLUMN] = str(n)

                    if subelem.tag == ENTRY:
                        txtvar = subelem.find(VARIABLE)
                        if txtvar is not None:
                            txtvar.attrib[NAME] =  subelem.attrib[attribName]

                    if not uniqueframe:
                        widget = self.processSubelement(fr.Frame, subelem)
                    else:
                        widget = self.processSubelement(mstrfr.Frame, subelem)

                except Exception as e:
                    print(e)
            if not uniqueframe:
                fr.layoutFrame()

        mstrfr.layoutFrame()





    def processXmlElement(self, master, element):
        varname = None
        args = None
        if element.tag == FORM:
            return self.processForm(master, element)

        elif element.tag == GROUP:
            return self.processGroup(master, element)

        elif element.tag == INCLUDE:
            return self.processIncludeTag(master, element)

        elif element.tag == REPGROUP:
            return self.processRepGroupTag(master, element)

        else:
            options = xlateArgs(self, element.attrib)

            if len(element) or element.tag in SPECIALTAGS:
                if element.tag == BUTTON:
                    options = self.processButtonOptions(element, options)
                    if NAME in options:
                        varname = options[NAME]
                        del(options[NAME])

                elif element.tag == ENTRY or element.tag == LABEL:
                    options = self.processEntryOptions(element, options)

                elif element.tag == CHECKBUTTON:
                    options = self.processCheckbuttonOptions(element, options)

                elif element.tag == RADIOBUTTON:
                    options = self.processRadiobuttonOptions(element, options)

                elif element.tag == SCALE:
                    options = self.processScaleOptions(element, options)

                elif element.tag == VARIABLE or element.tag == TEXTVARIABLE:
                    options = self.processVariableTagOptions(element, options)
                    return

                elif element.tag == OPTIONMENU:
                    if NAME in options:
                        varname = options[NAME]
                        del(options[NAME])
                    args = self.processMenuoptionOptions(element, options)

                elif element.tag == BIND:
                    self.processBindOptions(element, options)
                    return

                elif element.tag == CONFIGURE:
                    obj = element.attrib[OBJ]
                    obj.configure(command = element.attrib[COMMAND])
                    fnname = ""
                    tmp = str(element.attrib[COMMAND])
                    pos1 = tmp.find('.')
                    pos2 = tmp[pos1:].find(' ')
                    pos3 = tmp.rfind('!')
                    if pos1 > 0 and pos2 > 0 and pos3 > 0:
                        fnname = tmp[pos3+1:-2] + "." + tmp[pos1+1:pos2 + pos1]

                    emit(obj._name[1:] + ".configure(" + fnname + ")")
                    return

                for subelement in element:
                    if subelement.text is not None:
                        options[subelement.tag] = subelement.text

                    if COMMAND in options and TEXT in options and isinstance(options[COMMAND], str):
                        options[COMMAND] = self.makeCommand(options[COMMAND], self.processNoArg(options, options[TEXT]))

            if OPTIONMENU not in element.tag:
                widgetName = element.tag.capitalize()
            else:
                widgetName = 'OptionMenu'

            widgetlayout = LayoutManager(element, elementName=widgetName)
            try:
                widget_factory = GetAttr(mGraphicsLibName, widgetName)
            except:
                widget_factory = GetAttr(mttkGraphicsLibName, widgetName)

            if element.tag in SPECIALTAGS and NAME in options:
                varname = options[NAME]
                del options[NAME]

            if args is None:
                widget = widget_factory(master, **options)
            else:
                widget = widget_factory(master, *args, **options)

            emitWidget(widgetName, master, copy.copy(options))
            widgetlayout.applyLayoutToWidget(widget)
            if varname is not None:
                self.createAttr(varname, widget)

            return widget




class TkGUI_MakerMixin(GUI_MakerMixin):
    def __init__(self, topLevelWindow=None, outputfilename=None):
        super().__init__(topLevelWindow=topLevelWindow, outputfilename=outputfilename)

