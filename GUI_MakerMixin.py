#Gui_MakerMixin

import Tkinter
import xml.etree.ElementTree as ET
from functools import partial

#Special Tags
PACK = 'pack'
VARIABLE = 'variable'
TEXTVARIABLE = 'textvariable'
FORM = 'form'
GROUP = 'group'
CHECKBUTTON = 'checkbutton'
RADIOBUTTON = 'radiobutton'
BUTTON = 'button'

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



class GUI_MakerMixin(object):
    def __init__(self, topLevelWindow=None):
        if topLevelWindow is None:
            self.topLevelWindow = Tkinter.Tk()
        else:
            self.topLevelWindow = topLevelWindow

    def makeCommand(self, fnName, arg=None):
        """
        makeCommand takes fnName and turns it into an actual reference to the function
        :param fnName: str
        :param arg:
        :return: A reference to the actual function
        """
        if arg is None:
            return getattr(self, fnName)
        else:
            return partial(getattr(self, fnName), arg)

    def xlateArgs(self,kwargs):
        for key in kwargs:
            try:
                val = getattr(self,kwargs[key])
                kwargs[key] = val
            except:
                try:
                    val = getattr(Tkinter,kwargs[key])
                    kwargs[key] = val
                except:
                    pass

        return kwargs

    def parseXMLFile(self, xmlfile):
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        return root

    def makeGUI(self, master, xmlfile):
        element = self.parseXMLFile(xmlfile)
        frame = self.parseXmlElement(master, element)
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
                    func = getattr(Tkinter, fnName)

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
            packargs = self.xlateArgs(packelem.attrib.copy())
            elem.remove(packelem)
            return packargs


    def processForm(self, master, element):
        frameoptions = self.xlateArgs(element.attrib.copy())
        frame = Tkinter.Frame(master, **frameoptions)
        framepackargs = self.extractPackargs(element)

        packargs = None

        for subelement in element:
            packargs = self.extractPackargs(subelement)
            widget = self.parseXmlElement(frame, subelement)

            if packargs is None:
                widget.pack()
            else:
                widget.pack(**packargs)

        if framepackargs is None:
            frame.pack()
        else:
            frame.pack(**framepackargs)

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
        frame = Tkinter.Frame(master, **element.attrib)

        cblist = element.findall(CHECKBUTTON)
        if len(cblist) > 0:
            for cb in cblist:
                packargs = self.extractPackargs(cb)
                widget = self.parseXmlElement(frame, cb)
                element.remove(cb)

                # index = element._children.index(cb)
                # del(element._children[index])

                if packargs is None:
                    widget.pack()
                else:
                    widget.pack(**packargs)

        else:
            rblist = element.findall(RADIOBUTTON)
            if len(rblist) > 0:
                setattr(self, varname, varfunc)

                for rb in rblist:
                    packargs = self.extractPackargs(rb)
                    widget = self.parseXmlElement(frame, rb)
                    element.remove(rb)
                    # index = element._children.index(rb)
                    # del (element._children[index])

                    if packargs is None:
                        widget.pack()
                    else:
                        widget.pack(**packargs)

        if framepackargs is None:
            frame.pack()
        else:
            frame.pack(**framepackargs)

        return frame

    def processEntryOptions(self, element, options):
        textvar = element.find(TEXTVARIABLE)
        if textvar is not None:
            varfunc = getattr(Tkinter, textvar.attrib[TYPEVAR])()
            varname = textvar.attrib[NAME]
            setattr(self, varname, varfunc)
            options[TEXTVARIABLE] = varfunc
            element.remove(textvar)
            # index = element._children.index(textvar)
            # del(element._children[index])

        return options


    def processCheckbuttonOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            varfunc = getattr(Tkinter, optvar.attrib[TYPEVAR])()
            default = False
            if DEFAULT in optvar.attrib:
                default = optvar.attrib[DEFAULT]

            if default:
                varfunc.set(1)
            else:
                varfunc.set(0)

            varname = optvar.attrib[NAME]

            if ONCLICK in optvar.attrib:
                funcname = optvar.attrib[ONCLICK]
                options[COMMAND] = self.makeCommand(funcname, varname)

            setattr(self, varname, varfunc)
            options[VARIABLE] = varfunc
            index = element._children.index(optvar)
            del (element._children[index])

        return options

    def processRadiobuttonOptions(self, element, options):
        optvar = element.find(VARIABLE)
        if optvar is not None:
            varname = optvar.attrib[NAME]
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


    def parseXmlElement(self, master, element):
        framepackargs = None
        if element.tag == FORM:
            return self.processForm(master, element)

        elif element.tag == GROUP:
            return self.processGroup(master, element)

        else:
            options = element.attrib.copy()
            if len(options) > 0 and element.tag == BUTTON:
                if TEXT in options:
                    btnName = options[TEXT]

                    if COMMAND in options:
                        options[COMMAND] = self.makeCommand(options[COMMAND], btnName)
                else:
                    options = self.xlateArgs(options)

            if len(element):
                if element.tag == 'entry':
                    options = self.processEntryOptions(element, options)

                elif element.tag == 'checkbutton':
                    options = self.processCheckbuttonOptions(element, options)

                elif element.tag == 'radiobutton':
                    options = self.processRadiobuttonOptions(element, options)

                for subelement in element:
                    options[subelement.tag] = subelement.text

            widget_factory = getattr(Tkinter, element.tag.capitalize())
            return widget_factory(master, **options)

    def noop(self, *arg):
        """
        Sample onclick handler
        :param arg:
        :return:
        """
        if len(arg) == 1:
            if type(arg) == tuple:
                myarg = arg[0]
                # if isinstance(myarg, StringVarPlus):
                #     myarg = myarg.get()
            else:
                myarg = arg
        else:
            myarg = arg[0]
        print("noop called: %s" % myarg)

if __name__ == '__main__':
    root = Tkinter.Tk()
    root.geometry("230x200")

    m1 = GUI_MakerMixin(root)
    fr = m1.makeGUI(root, "gui1.xml")
    fr.pack()

    root.mainloop()
