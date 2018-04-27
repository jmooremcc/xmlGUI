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
        
    <menuitem name='' onclick='' shortcutindex="" />
            name is menuitem name
            onclick is name of function to call when the item is clicked and must be in the current scope
                The function called will receive the item name as a parameter.
            shortcutindex is the index of the letter in the menuitem name to use as an accellerator
            Note: both onclick and shortcutindex must be defined to activate the accellerator
    </menu>
    
    <optionmenu name='' id='' dataprovider='' typebutton=""/>
            name is optionmenu name
            id is the name to use for the dynamically created variable name that represents the optionmenu
            dataprovider is the function that will load the options
               if dataprovider is missing, radioitems should be used to provide the options
            typebutton is the type of button to create. By default it's a radiobutton. If you specify a checkbutton,
                you'll get a checkbutton created.
            
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


class MenuMakerMixin(object):
    def __init__(self, topLevelWidget):
        self._topLevelWidget = topLevelWidget
        self._optionMenusList = {}
        self._optionCount = 0
        self.topmenu = None

    def generateMenu(self, xmlfile, parent=None):
        tree = ET.parse(xmlfile)
        self.root = tree.getroot()
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

    def processChildElement(self, newMenu, child, optionButtonOptvar=None):
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

            return

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
            try:
                cbflag = self.getOptionMenuType(newMenu) == CHECKBUTTONITEM
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

                    return

                # else:
                    # newMenu.add_radiobutton(**kwargs)
                    # if DEFAULT in child.attrib:
                    #     optvar.set(kwargs[VALUE])

            except Exception as e:
                pass
                # newMenu.add_radiobutton(**kwargs)
                # if DEFAULT in child.attrib:
                #     optvar.set(kwargs[VALUE])
        """
            option item is a radiobutton
        """
        newMenu.add_radiobutton(**kwargs)
        if DEFAULT in child.attrib:
            optvar.set(kwargs[VALUE])


    def processOptionMenu(self, parent, optmenu, child):
        id = child.attrib[ID]

        if len(child) == 0:
            funcName = None
            if ONCLICK in child.attrib:
                funcName = child.attrib[ONCLICK]

            if DATAPROVIDER in child.attrib:
                dataprovider = child.attrib[DATAPROVIDER]

            optvar = StringVarPlus()
            self.addOptionVarRef(optvar, id)
            self.__getattribute__(dataprovider)(optvar, optmenu, funcName, id)
            # self.fillOptionValues(newMenu,self.noop)
        else:
            try:
                cbflag = self.getOptionMenuType(optmenu) == CHECKBUTTONITEM
                if cbflag:
                    for childopt in child:
                        optvar = StringVarPlus()
                        self.addOptionVarRef(optvar, id)
                        self.processChildElement(optmenu, childopt, optionButtonOptvar=optvar)
                else:
                    optvar = StringVarPlus()
                    self.addOptionVarRef(optvar, id)
                    for childopt in child:
                        self.processChildElement(optmenu, childopt, optionButtonOptvar=optvar)

            except:
                optvar = StringVarPlus()
                self.addOptionVarRef(optvar, id)
                for childopt in child:
                    self.processChildElement(optmenu, childopt, optionButtonOptvar=optvar)


    def menuTag(self, parent, elem):
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

        for child in elem:
            if child.tag == MENU:
                self.parseMenuTree(newMenu, child)

            elif child.tag == SEPARATOR:
                newMenu.add_separator()

            elif child.tag == OPTIONMENU:
                # id=elem.attrib[ID]
                optmenu = Menu(parent, tearoff=0)

                if TYPEBUTTON in child.attrib:
                    self.setOptionMenuType(newMenu, child.attrib[TYPEBUTTON])

                newMenu.add_cascade(label=child.attrib[NAME], menu=optmenu)
                self.processOptionMenu(parent, optmenu, child)

            elif child.tag == MENUITEM:
                self.processChildElement(newMenu, child)


    def processSiblings(self, parent, elem):
        for child in elem:
            if child.tag == MENUITEM:
                self.processChildElement(parent, child)
            else:
                self.parseMenuTree(parent, child)


    def menusTag(self, parent, elem):
        self.processSiblings(parent, elem)


    def menuitemTag(self, parent, elem):
        pass


    def getOptionMenuType(self, optmenu):
        return optmenu.__dict__[TYPEBUTTON]


    def setOptionMenuType(self, optmenu, value):
        optmenu.__dict__[TYPEBUTTON] = value


    def optionmenuTag(self, parent, elem):
        id = elem.attrib[ID]
        menuName = elem.attrib[NAME]
        optmenu = Menu(parent, tearoff=0)
        # self.optionMenusList[id]=optmenu
        if TYPEBUTTON in elem.attrib:
            self.setOptionMenuType(optmenu, elem.attrib[TYPEBUTTON])

        parent.add_cascade(label=menuName, menu=optmenu)
        self.processOptionMenu(parent, optmenu, elem)


    def menubuttonTag(self, parent, elem):
        kwargs = elem.attrib
        imageFile = kwargs[IMAGE]
        menuName = kwargs[NAME]
        kwargs[RELIEF] = Tkconstants.__getattribute__(kwargs[RELIEF])
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

        self.processSiblings(menu, elem)

        mb.pack(side=LEFT, fill=BOTH)
        frame.pack(side=TOP, fill=BOTH)


    def parseMenuTree(self, parent, elem):
        dispatcher = {
            MENUS: self.menusTag,
            MENU: self.menuTag,
            MENUBUTTON: self.menubuttonTag,
            OPTIONMENU: self.optionmenuTag
        }
        try:
            dispatcher[elem.tag](parent, elem)
        except Exception as e:
            raise Exception("tag: %s is not a menu tag" % elem.tag)


    def fillOptionValues(self, optvar, optmenu, callback, id):
        values = ['OE2', 'OE3', 'LocalHost']
        optvar.set(values[0])

        try:
            cbflag = self.getOptionMenuType(optmenu) == CHECKBUTTONITEM
            if cbflag:
                for n, item in enumerate(values):
                    optvar = StringVarPlus()
                    self.addOptionVarRef(optvar, id)

                    if callback is None:
                        optmenu.add_checkbutton(label=item, variable=optvar, onvalue="%s:%s" % (item, True),
                                                offvalue="%s:%s" % (item, False))
                    else:
                        optmenu.add_checkbutton(label=item, variable=optvar, onvalue="%s:%s" % (item, True),
                                                offvalue="%s:%s" % (item, False),
                                                command=self.makeCommand(callback, optvar))

                    if n == 0:
                        optvar.set("%s:%s" % (item, True))
                    else:
                        optvar.set("%s:%s" % (item, False))
            else:
                for item in values:
                    optmenu.add_radiobutton(label=item, variable=optvar, value=item,
                                            command=self.makeCommand(callback, optvar))
        except Exception as e:
            for item in values:
                optmenu.add_radiobutton(label=item, variable=optvar, value=item,
                                        command=self.makeCommand(callback, optvar))


    def noop(self, *arg):
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
        exit()


def createIcon(imgFilename):
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
