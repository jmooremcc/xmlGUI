#MenuMakerMixin

import xml.etree.ElementTree as ET
from Tkinter import *
from functools import partial
from PIL import Image, ImageTk
import Tkconstants
from time import sleep

"""
<menus>
    <menu name='' type=''>
        name is menu name
        type is ...
        
        <menuitem name='' onclick='' shortcutindex="" />
            name is menuitem name
            onclick is name of function to call when the item is clicked and must be in the current scope
            shortcutindex is the index of the letter in the menuitem name to use as an accellerator
            Note: both onclick and shortcutindex must be defined to activate the accellerator
    </menu>
    <optionmenu name='' id='' dataprovider=''/>
            name is optionmenu name
            id is the name to use for the dynamically created variable name that represents the optionmenu
            dataprovider is the function that will load the options
               if dataprovider is missing, radioitems should be used to provide the options
            
               
         <radioitem name='' value='' onclick='' default=''/>
            name is the radioitem name
            value is the data to pass as an argument to the onclick function
            onclick is the function to call when the item is clicked and must be in the current scope
             The onclick function should accept a string parm that represents option selected
            default if present indicates this item is the default item and will display a check mark
        .
        .
        .
</menus>
"""

#Tag Constants
MENUS           = 'menus'
MENU            = 'menu'
MENUBUTTON      = 'menubutton'
MENUITEM        = 'menuitem'
OPTIONMENU      = 'optionmenu'
RADIOITEM       = 'radioitem'
SEPARATOR       = 'separator'
# PACKARGS        = 'packargs'
# Attribute Constants
NAME            = 'name'
TYPE            = 'type'
ONCLICK         = 'onclick'
ID              = 'id'
DEFAULT         = 'default'
VALUE           = 'value'
DATAPROVIDER    = 'dataprovider'
IMAGE           = 'image'
UNDERLINE       = 'underline'
SHORTCUTINDEX   = 'shortcutindex'
COMMAND         = 'command'
RELIEF          = 'relief'
VARIABLE        = 'variable'

class MenuMakerMixin(object):
    def __init__(self, topLevelWidget):
        self.topLevelWidget = topLevelWidget

    def generateMenu(self,xmlfile, parent=None ):
        tree = ET.parse(xmlfile)
        self.root = tree.getroot()
        if self.root.tag != MENUS:
            raise Exception("%s does not contain the required menus tag" % xmlfile)

        self.topmenu = None

        if self.root[0].tag == MENUBUTTON:
            self.parseMenuTree(parent, self.root)
        else:
            menu = Menu(parent, tearoff=0)
            self.parseMenuTree(menu, self.root)
            if parent is not None:
                parent.config(menu=menu)

            return menu

    def makeCommand(self, fnName, arg=None):
        return partial(self.__getattribute__(fnName), arg)

    def processChildElement(self, newMenu, child, radiobuttonoptvar=None):
            menuItemName = child.attrib[NAME]
            kwargs = {}
            kwargs['label'] = menuItemName

            if radiobuttonoptvar == None:
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
                        self.topLevelWidget.bind_all("<Control-%s>" % ch.lower(), kwargs[COMMAND])

                newMenu.add_command(**kwargs)

            else:
                optvar=radiobuttonoptvar
                kwargs[VARIABLE] = optvar
                kwargs[VALUE] = child.attrib[VALUE]

                if ONCLICK in child.attrib:
                    callback = child.attrib[ONCLICK]
                    kwargs[COMMAND] = self.makeCommand(callback, kwargs[VALUE])

                print("option-kwargs: %s" % kwargs)
                newMenu.add_radiobutton(**kwargs)

                if DEFAULT in child.attrib:
                    optvar.set(kwargs[VALUE])

    def processOptionMenu(self, parent, optmenu, child):
        id = child.attrib[ID]
        setattr(self, id, optmenu)
        optvar = StringVar()
        setattr(self, id + 'Var', optvar)

        if len(child) == 0:
            if DATAPROVIDER in child.attrib:
                funcName = child.attrib[DATAPROVIDER]
                self.__getattribute__(funcName)(optvar, optmenu, self.noop)
            # self.fillOptionValues(newMenu,self.noop)
        else:
            for childopt in child:
                self.processChildElement(optmenu, childopt, radiobuttonoptvar=optvar)


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
                optmenu = Menu(parent, tearoff=0)
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

    def optionmenuTag(self, parent, elem):
        menuName = elem.attrib[NAME]
        optmenu = Menu(parent, tearoff=0)
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
            OPTIONMENU: self.optionmenuTag,
            MENUITEM: None,
            RADIOITEM: None,
            SEPARATOR: None
        }
        try:
            dispatcher[elem.tag](parent, elem)
        except:
            raise Exception("tag: %s is not a menu tag" % elem.tag)



    def fillOptionValues(self, optvar, optmenu, callback):
        values=['OE2','OE3','LocalHost']
        optvar.set(values[0])

        for item in values:
            optmenu.add_radiobutton(label=item, variable=optvar, value=item,
                                             command=lambda: callback(optvar.get()))

    def noop(self, *arg):
        if len(arg) == 1:
            myarg=arg
        else:
            myarg=arg[0]
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
    val=m1.generateMenu("menu.xml", root)
    # m1.generateMenu("menu2.xml", root)
    m1.generateMenu("menu3.xml", root)
    popupMenu = m1.generateMenu("menu4.xml")
    def popup(*args):
        if len(args) == 2:
            popupMenu.post(args[0], args[1])
        else:
            event = args[0]
            popupMenu.post(event.x_root, event.y_root)

    b=Button(root,text="Popup Menu")
    b.pack()
    b[COMMAND]=lambda: popup(b.winfo_rootx()+30, b.winfo_rooty()+20)
    root.bind_all('<Button-3>',popup)
    root.mainloop()
