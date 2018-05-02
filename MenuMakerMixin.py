# MenuMakerMixin

import xml.etree.ElementTree as ET
from Tkinter import *
from functools import partial
from PIL import Image, ImageTk
import Tkconstants
from time import sleep
from StringVarPlus import StringVarPlus

"""
<menus>
    <menu name='' type=''>
        name is menu name
        type is ...
        
    <menubutton name="" bg="" image="" relief="" activebackground="" />
        <pack side='' fill=''/>
    
    <menuitem name='' onclick='' shortcutindex="" />
            name is menuitem name
            onclick is name of function to call when the item is clicked and must be in the current scope
                The function called will receive the item name as a parameter.
            shortcutindex is the index of the letter in the menuitem name to use as an accellerator
            Note: both onclick and shortcutindex must be defined to activate the accellerator
    </menu>
    
    <optionmenu name='' id='' dataprovider='' typebutton="" defaultindex=""/>
            name is optionmenu name
            id is the name to use for the dynamically created variable name that represents the optionmenu
            dataprovider is the function that will load the options
               if dataprovider is missing, radioitems should be used to provide the options
            typebutton is the type of button to create. By default it's a radiobutton. If you specify a checkbutton,
                you'll get a checkbutton created.
            defaultindex is the index of the default item if the data comes from a datasource
            
    <optionitem name='' value='' onclick='' default=''/>
            name is the optionitem name
            value is the data to pass as an argument to the onclick function
            In the case of a checkbutton, the optvar will be passed to the function
            onclick is the function to call when the item is clicked and must be in the current scope
                The onclick function should accept a string parm that represents option selected
                default if present indicates this item is the default item and will display a check mark
        .
        .
        .
</menus>
"""

# Menu Tags
MENUS = 'menus'
MENU = 'menu'
MENUBUTTON = 'menubutton'
INCLUDE = 'include'
# SubMenu Tags
MENUITEM = 'menuitem'
OPTIONMENU = 'optionmenu'
OPTIONITEM = 'optionitem'
CHECKBUTTONITEM = 'checkbuttonitem'
SEPARATOR = 'separator'
# PACKARGS        = 'packargs'
# Attribute Tags
NAME = 'name'
TYPE = 'type'
ONCLICK = 'onclick'
ID = 'id'
DEFAULT = 'default'
VALUE = 'value'
DATAPROVIDER = 'dataprovider'
IMAGE = 'image'
UNDERLINE = 'underline'
SHORTCUTINDEX = 'shortcutindex'
COMMAND = 'command'
RELIEF = 'relief'
VARIABLE = 'variable'
TYPEBUTTON = 'typebutton'
LABEL = 'label'
DEFAULTINDEX = 'defaultindex'
PACK='pack'
FILENAME = 'filename'


class MenuMakerMixin(object):
    def __init__(self, topLevelWidget):
        self._topLevelWidget = topLevelWidget
        self._optionMenusList = {}
        self._optionCount = 0
        self.topmenu = None

    def parseXMLFile(self, xmlfile):
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        return root

    def generateMenu(self, xmlfile, parent=None):
        self.root = self.parseXMLFile(xmlfile)

        if self.root.tag != MENUS:
            raise Exception("%s does not contain the required menus tag" % xmlfile)

        if self.root[0].tag == MENUBUTTON:
            self.parseMenuTree(parent, self.root)
        else:
            menu = Menu(parent, tearoff=0)
            self.parseMenuTree(menu, self.root)
            if parent is not None:
                parent.config(menu=menu)

            return menu

    def xlateArgs(self,kwargs):
        import Tkinter

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

    def addOptionVarRef(self, optionVar, optionName):
        name = "%sVar%d" % (optionName, self._optionCount)
        optionVar.Name = name
        self._optionMenusList[name] = optionVar
        self._optionCount += 1

    def getOptionVars(self, id="_ALL_"):
        if id == "_ALL_":
            return self._optionMenusList.values()

        tmplist = {}
        olist = self._optionMenusList
        for key in olist:
            if id in key:
                tmplist[key] = olist[key]

        return tmplist

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

    def processChildElement(self, newMenu, child, optionButtonOptvar=None, cbflag=False):
        """
        Converts attributes into kwargs and adds a command to newMenu object
        :param newMenu: Menu
        :param child: element
        :param optionButtonOptvar: StringVarPlus
        :return: 
        """""

        menuItemName = child.attrib[NAME]
        kwargs = {}
        kwargs['label'] = menuItemName

        if optionButtonOptvar == None:
            """
                Process regular menu item
            """
            shortcutIndex = False
            if SHORTCUTINDEX in child.attrib:
                shortcutIndex = True
                chIndex = int(child.attrib[SHORTCUTINDEX])
                ch = menuItemName[chIndex].upper()
                kwargs['accelerator'] = "Ctrl+" + ch
                kwargs[UNDERLINE] = chIndex

            if ONCLICK in child.attrib:
                onclickCallbackName = child.attrib[ONCLICK]
                kwargs[COMMAND] = self.makeCommand(onclickCallbackName, menuItemName)
                if shortcutIndex:
                    self._topLevelWidget.bind_all("<Control-%s>" % ch.lower(), kwargs[COMMAND])

            newMenu.add_command(**kwargs)

        else:
            """
                Process option menu - either radiobutton or checkbutton
            """
            optvar = optionButtonOptvar
            kwargs[VARIABLE] = optvar
            value = kwargs[VALUE] = child.attrib[VALUE]

            if ONCLICK in child.attrib:
                callback = child.attrib[ONCLICK]
                kwargs[COMMAND] = self.makeCommand(callback, kwargs[VALUE])

            print("option-kwargs: %s" % kwargs)

            if cbflag:
                """
                    option item is a checkbutton
                """
                kwargs['onvalue'] = "%s:%s" % (value, True)
                kwargs['offvalue'] = "%s:%s" % (value, False)
                del (kwargs[VALUE])
                if DEFAULT in child.attrib:
                    optvar.set(kwargs['onvalue'])
                else:
                    optvar.set(kwargs['offvalue'])

                if COMMAND in kwargs:
                    kwargs[COMMAND] = self.makeCommand(callback, optvar)

                newMenu.add_checkbutton(**kwargs)

            else:
                newMenu.add_radiobutton(**kwargs)
                if DEFAULT in child.attrib:
                    optvar.set(value)




    def processOptionMenu(self, parent, optmenu, child, cbflag):
        """
        Process either radiobutton or checkbutton option
        :param parent: Menu
        :param optmenu: Menu
        :param child: element
        :return:
        """
        id = child.attrib[ID]
        kwargs = {}

        if len(child) == 0:
            """
                Call a data provider since no children exist to provide options
            """

            if DATAPROVIDER in child.attrib:
                if ONCLICK in child.attrib:
                    funcName = child.attrib[ONCLICK]
                    kwargs[COMMAND]=self.makeCommand(funcName)

                try:
                    dataprovider = self.makeCommand(child.attrib[DATAPROVIDER])
                    olist = dataprovider()

                except Exception as e:
                    print e.message
                    raise(e)

                defaultindex = 0
                if DEFAULTINDEX in child.attrib:
                    defaultindex = int(child.attrib[DEFAULTINDEX])

                if cbflag:
                    for n, opName in enumerate(olist):
                        kwargs['onvalue'] = "%s:%s" % (opName, True)
                        kwargs['offvalue'] = "%s:%s" % (opName, False)
                        optvar = StringVarPlus()
                        kwargs[VARIABLE] = optvar
                        self.addOptionVarRef(optvar, id)
                        kwargs[LABEL] = kwargs[VALUE] = opName
                        if n == defaultindex:
                            optvar.set(kwargs['onvalue'])
                        else:
                            optvar.set(kwargs['offvalue'])

                        optmenu.add_checkbutton(**kwargs)
                else:
                    try:
                        optvar = StringVarPlus()
                        kwargs[VARIABLE] = optvar
                        self.addOptionVarRef(optvar, id)
                        if COMMAND in kwargs:
                            kwargs[COMMAND] = self.makeCommand(funcName, optvar)

                        for n, opName in enumerate(olist):
                            kwargs[LABEL] = kwargs[VALUE] = opName
                            if n == defaultindex:
                                optvar.set(olist[n])

                            optmenu.add_radiobutton(**kwargs)
                    except Exception as e:
                        pass
        else:
            """
                The options are provided by child optionitems
            """
            if cbflag:
                for childopt in child:
                    optvar = StringVarPlus()
                    self.addOptionVarRef(optvar, id)
                    self.processChildElement(optmenu, childopt, optionButtonOptvar=optvar, cbflag=cbflag)
            else:
                optvar = StringVarPlus()
                self.addOptionVarRef(optvar, id)
                for childopt in child:
                    self.processChildElement(optmenu, childopt, optionButtonOptvar=optvar, cbflag=cbflag)



    def menuTag(self, parent, elem):
        """
        Process a menu tag by creating an instance of the Menu class and adds it as a submenu (cascade) to the parent
        The function then processes the following child elements:
            SEPARATOR tags
                adds a separator to the menu
            OPTIONMENU tags
                call processOptionMenu to process option
            MENU tags
                call parseMenuTree recursively to handle it
            MENUITEM tags
                call processChildElement to handle it

        :param parent: Menu
        :param elem: Element
        :return:
        """
        print("menu: %s " % elem.tag)
        menuName = elem.attrib[NAME]
        newMenu = Menu(parent, tearoff=0)

        if self.topmenu is None:
            self.topmenu = newMenu

        parent.add_cascade(label=menuName, menu=newMenu)
        print("menuName: %s" % menuName)
        if TYPE in elem.attrib:
            menuType = elem.attrib[type]
            print("menu type is %s" % menuType)
        else:
            pass

        #Process Child Elements
        for child in elem:
            if child.tag == MENU:
                self.parseMenuTree(newMenu, child)

            elif child.tag == SEPARATOR:
                newMenu.add_separator()

            elif child.tag == OPTIONMENU:
                # id=elem.attrib[ID]
                optmenu = Menu(parent, tearoff=0)

                cbflag = False
                if TYPEBUTTON in child.attrib:
                    if child.attrib[TYPEBUTTON] == CHECKBUTTONITEM:
                        cbflag = True

                newMenu.add_cascade(label=child.attrib[NAME], menu=optmenu)
                self.processOptionMenu(parent, optmenu, child, cbflag)

            elif child.tag == INCLUDE:
                self.includeTag(newMenu, child)

            elif child.tag == MENUITEM:
                self.processChildElement(newMenu, child)


    def processSiblings(self, parent, elem):
        """
        Process an Element's children
        if a non MENUITEM element is found, call parseMenuTree to handle it
        :param parent: Menu
        :param elem: Element
        :return:
        """
        for child in elem:
            if child.tag == MENUITEM:
                self.processChildElement(parent, child)
            else:
                self.parseMenuTree(parent, child)


    def menusTag(self, parent, elem):
        self.processSiblings(parent, elem)


    def menuitemTag(self, parent, elem):
        pass


    # def getOptionMenuType(self, optmenu):
    #     return optmenu.__dict__[TYPEBUTTON]
    #
    #
    # def setOptionMenuType(self, optmenu, value):
    #     optmenu.__dict__[TYPEBUTTON] = value


    def optionmenuTag(self, parent, elem):
        """
        Create a new Menu object and add it to the parent as a submenu
        call processOptionMenu to process options
        :param parent: Menu
        :param elem: Element
        :return:
        """
        id = elem.attrib[ID]
        menuName = elem.attrib[NAME]
        optmenu = Menu(parent, tearoff=0)
        cbflag=False
        if elem.attrib[TYPEBUTTON] == CHECKBUTTONITEM:
            cbflag = True

        parent.add_cascade(label=menuName, menu=optmenu)
        self.processOptionMenu(parent, optmenu, elem, cbflag)


    def menubuttonTag(self, parent, elem):
        """
        Create a menubutton object with the image specified in the attributes
        processSiblings is then called to process any child options
        :param parent: Menu
        :param elem: Element
        :return:
        """
        kwargs = elem.attrib
        imageFile = kwargs[IMAGE]
        menuName = kwargs[NAME]
        kwargs[RELIEF] = getattr(Tkconstants,kwargs[RELIEF])
        kwargs[NAME] = menuName.lower()
        icon = createIcon(imageFile)
        kwargs[IMAGE] = icon

        frame = Frame(parent)
        # mb = Menubutton(frame, bg='sky blue', relief=RIDGE, activebackground='green')
        mb = Menubutton(frame, **kwargs)
        mb['text'] = 'XXX'
        mb.menu = menu = Menu(mb, tearoff=0)
        mb["menu"] = mb.menu
        mb["image"] = icon
        setattr(self, menuName + "Img", icon)
        mb.config(image=icon)

        packargs = None
        if PACK in elem[0].tag:
            packargs = self.xlateArgs(elem[0].attrib.copy())
            elem = elem[1:]

        self.processSiblings(menu, elem)

        mb.pack(side=LEFT, fill=BOTH)
        if packargs is None:
            frame.pack(side=TOP, fill=BOTH)
        else:
            frame.pack(packargs)
        #TODO add PACKARGS item to control how the frame is packed

    def includeTag(self, parent, elem):
        if FILENAME in elem.attrib:
            filename = elem.attrib[FILENAME]
            elem = self.parseXMLFile(filename)
            self.parseMenuTree(parent, elem)

    def parseMenuTree(self, parent, elem):
        """
        This is a dispatcher function that calls the appropriate functions based on the element tag
        :param parent: Menu or Window
        :param elem: Element
        :return:
        """
        dispatcher = {
            MENUS: self.menusTag,
            MENU: self.menuTag,
            MENUBUTTON: self.menubuttonTag,
            OPTIONMENU: self.optionmenuTag,
            INCLUDE:self.includeTag
        }
        try:
            dispatcher[elem.tag](parent, elem)
        except Exception as e:
            print("%s is not a menu tag" % elem.tag)
            raise Exception("%s is not a menu tag" % elem.tag)


    def myDataprovider(self):
        """
        Sample dataprovider simulating getting option data from an external source
        :return: list[str]
        """
        values = ['OE2', 'OE3', 'LocalHost']
        return values



    def noop(self, *arg):
        """
        Sample onclick handler
        :param arg:
        :return:
        """
        if len(arg) == 1:
            if type(arg) == tuple:
                myarg = arg[0]
                if isinstance(myarg, StringVarPlus):
                    myarg = myarg.get()
            else:
                myarg = arg
        else:
            myarg = arg[0]
        print("noop called: %s" % myarg)


    def quit(self, *arg):
        """
        Sample onclick handler
        :param arg:
        :return:
        """
        exit()

    def dumpOptvars(self, opt):
        olist = self.getOptionVars()
        print ""
        for v in olist:
            print "%s:%s" % (v.Name, v.get())

def createIcon(imgFilename):
    """
    Converts an image into a bitmap that can be used on a menubutton
    :param imgFilename: str
    :return: ImageTk.PhotoImage
    """
    image = Image.open(imgFilename)
    image2 = image.resize((30, 30), Image.ANTIALIAS)
    # setattr(self, iconVarname, ImageTk.PhotoImage(image))
    return ImageTk.PhotoImage(image2)


if __name__ == "__main__":
    root = Tk()
    root.geometry("230x100")
    # icon = createIcon('gearIcon.png')

    # frame = Frame(root)
    # mb = Menubutton(frame, bg='sky blue', image=icon, relief=RIDGE, activebackground='green')
    # # mb.menu = Menu(mb, tearoff=0)
    # # mb.menu.add_command(label="myTest")
    # mb.pack(side=LEFT, fill=BOTH)
    # setattr(self, name, mb)
    # parent.add_cascade(menu=mb)
    # frame.pack(side=TOP, fill=BOTH)
    m1 = MenuMakerMixin(root)
    # m1.generateMenu("menu2.xml", root)
    val = m1.generateMenu("menu.xml", root)
    # m1.generateMenu("menu2.xml", root)
    m1.generateMenu("menu3.xml", root)
    popupMenu = m1.generateMenu("menu4.xml")


    def popup(*args):
        if len(args) == 2:
            popupMenu.post(args[0], args[1])
        else:
            event = args[0]
            popupMenu.post(event.x_root, event.y_root)


    b = Button(root, text="Popup Menu")
    b.pack()
    b[COMMAND] = lambda: popup(b.winfo_rootx() + 30, b.winfo_rooty() + 20)
    root.bind_all('<Button-3>', popup)
    root.mainloop()
