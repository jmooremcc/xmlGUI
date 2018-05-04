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

#Special Attributes
ONCLICK = 'onclick'
COMMAND = 'command'
TYPEVAR = 'typevar'
NAME = 'name'
GROUPLIST = 'grouplist'
DEFAULT = 'default'
VARNAME = 'varname'
VALUE = 'value'



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
            return self.__getattribute__(fnName)
        else:
            return partial(self.__getattribute__(fnName), arg)

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

    def parseXmlElement(self, master, element):
        framepackargs = None
        if element.tag == FORM:
            frame = Tkinter.Frame(master, **element.attrib)
            if len(element) > 0 and PACK in element[0].tag:
                framepackargs = self.xlateArgs(element[0].attrib.copy())
                element._children = element[1:]

            packargs = None

            for subelement in element:
                if len(subelement) > 0 and PACK in subelement[0].tag:
                    packargs = self.xlateArgs(subelement[0].attrib.copy())
                    subelement._children = subelement[1:]

                widget = self.parseXmlElement(frame, subelement)

                if packargs is None:
                    widget.pack()
                else:
                    widget.pack(**packargs)
            return frame

        elif element.tag == GROUP:
            cblist = None
            rblist = None
            grpname = element.attrib[NAME]
            del (element.attrib[NAME])
            grplistname = element.attrib[GROUPLIST]
            del (element.attrib[GROUPLIST])
            cblist = element.findall(CHECKBUTTON)
            if ONCLICK in element.attrib:
                onclickfunc = element.attrib[ONCLICK]
                del (element.attrib[ONCLICK])

            varfunc = None
            varname = None

            if VARNAME in element.attrib:
                varname = element.attrib[VARNAME]
                del (element.attrib[VARNAME])

            if TYPEVAR in element.attrib:
                varfunc = getattr(Tkinter, element.attrib[TYPEVAR])()
                del(element.attrib[TYPEVAR])

            frame = Tkinter.Frame(master, **element.attrib)

            if len(cblist) > 0:
                packargs = None
                for cb in cblist:
                    if len(cb) > 0 and PACK in cb[0].tag:
                        packargs = self.xlateArgs(cb[0].attrib.copy())
                        cb._children = cb[1:]
                    widget = self.parseXmlElement(frame, cb)
                    # funcname = self.makeCommand(onclickfunc,widget.config('text')[4])
                    index = element._children.index(cb)
                    del(element._children[index])

                    if packargs is None:
                        widget.pack()
                    else:
                        widget.pack(**packargs)

            else:
                rblist = element.findall(RADIOBUTTON)
                if len(rblist) > 0:
                    packargs = None


                    setattr(self,varname, varfunc)

                    for rb in rblist:
                        if len(rb) > 0 and PACK in rb[0].tag:
                            packargs = self.xlateArgs(rb[0].attrib.copy())
                            rb._children = rb[1:]
                        widget = self.parseXmlElement(frame, rb)

                        index = element._children.index(rb)
                        del (element._children[index])

                        if packargs is None:
                            widget.pack()
                        else:
                            widget.pack(**packargs)

            return frame

        else:
            options = element.attrib
            if len(options) > 0:
                options = options.copy()
                if COMMAND in options:
                    options[COMMAND] = self.makeCommand(options[COMMAND],'OK')

            if len(element):
                if element.tag == 'entry':
                    textvar = element.find(TEXTVARIABLE)
                    if textvar is not None:
                        varfunc = getattr(Tkinter, textvar.attrib[TYPEVAR])()
                        varname = textvar.attrib[NAME]
                        setattr(self,varname,varfunc)
                        options[TEXTVARIABLE]= varfunc
                        index = element._children.index(textvar)
                        del(element._children[index])

                elif element.tag == 'checkbutton':
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
                            funcname=optvar.attrib[ONCLICK]
                            options[COMMAND] = self.makeCommand(funcname,varname)

                        setattr(self, varname, varfunc)
                        options[VARIABLE] = varfunc
                        index = element._children.index(optvar)
                        del (element._children[index])

                elif element.tag == 'radiobutton':
                    optvar = element.find(VARIABLE)
                    if optvar is not None:
                        # varfunc = getattr(Tkinter, optvar.attrib[TYPEVAR])()
                        varname = optvar.attrib[NAME]
                        varfunc = getattr(self, varname)

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

                        # setattr(self, varname, varfunc)
                        options[VARIABLE] = varfunc
                        index = element._children.index(optvar)
                        del (element._children[index])

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
    root.geometry("230x150")

    m1 = GUI_MakerMixin(root)
    fr = m1.makeGUI(root, "gui1.xml")
    fr.pack()

    root.mainloop()
