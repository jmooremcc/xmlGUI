#MenuMakerMixin

import xml.etree.ElementTree as ET
from Tkinter import *
from functools import partial
from PIL import Image, ImageTk

"""
<menus>
    <menu name='' type=''>
        <menuitem name='' onclick='' />
    </menu>
    <optionmenu name='' id='' default='' dataprovider=''/>
         <radioitem name='' value='' onclick='' default=''/>
        .
        .
        .
</menus>
"""

#Tag Constants
MENU            = 'menu'
MENUS           = 'menus'
MENUITEM        = 'menuitem'
OPTIONMENU      = 'optionmenu'
RADIOITEM       = 'radioitem'
MENUBUTTON      = 'menubutton'
# Attribute Constants
NAME            = 'name'
TYPE            = 'type'
ONCLICK         = 'onclick'
ID              = 'id'
DEFAULT         = 'default'
VALUE           = 'value'
DATAPROVIDER    = 'dataprovider'
IMAGE           = 'image'

class MenuMakerMixin(object):
    def generateMenu(self, parent, xmlfile):
        tree = ET.parse(xmlfile)
        self.root = tree.getroot()
        if self.root.tag != MENUS:
            raise Exception("%s does not containthe required menus tag" % xmlfile)

        self.menuItems={}
        menu = Menu(parent, tearoff=0)
        self.parseMenuTree(menu,self.root)
        parent.config(menu=menu)
        # if self.__getattribute__('mb'):
        #     return self.mb

    def makeCommand(self, fnName, arg):
        return partial(self.__getattribute__(fnName), arg)




    def processChildElement(self, newMenu, child, radiobuttonoptvar=None):
            menuItemName = child.attrib[NAME]
            kwargs = {}
            kwargs['label'] = menuItemName

            if radiobuttonoptvar == None:
                shortcut = None
                if 'shortcut' in child.attrib:
                    shortcut = child.attrib['shortcut']
                    kwargs['accelerator'] = shortcut
                    kwargs['underline'] = 0

                if ONCLICK in child.attrib:
                    onclickCallbackName = child.attrib[ONCLICK]
                    kwargs['command'] = self.makeCommand(onclickCallbackName, menuItemName)

                newMenu.add_command(**kwargs)

            else:
                optvar=radiobuttonoptvar
                kwargs['variable'] = optvar
                kwargs[VALUE] = child.attrib[VALUE]

                if ONCLICK in child.attrib:
                    callback = child.attrib[ONCLICK]
                    kwargs['command'] = self.makeCommand(callback, kwargs[VALUE])

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




    def parseMenuTree(self, parent, elem):
        if elem.tag == MENU:
            print("menu: %s " % elem.tag)
            menuName = elem.attrib[NAME]
            newMenu = Menu(parent, tearoff=0)
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

                elif child.tag == 'separator':
                    newMenu.add_separator()

                elif child.tag == OPTIONMENU:
                    optmenu = Menu(parent, tearoff=0)
                    newMenu.add_cascade(label=child.attrib[NAME], menu=optmenu)
                    self.processOptionMenu(parent, optmenu, child)
                else:
                    self.processChildElement(newMenu, child)

        elif elem.tag == MENUS:
            for child in elem:
                if child.tag == MENUITEM:
                    self.processChildElement(parent, child)
                else:
                    self.parseMenuTree(parent, child)

        elif elem.tag == OPTIONMENU:
            menuName = elem.attrib[NAME]
            optmenu = Menu(parent, tearoff=0)
            parent.add_cascade(label=menuName, menu=optmenu)
            self.processOptionMenu(parent, optmenu, elem)

        else:
           raise Exception("tag: %s is not a menu tag" % elem.tag)
           #  self.processChildElement(parent, elem)

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
    image = image.resize((30, 30), Image.ANTIALIAS)
    # setattr(self, iconVarname, ImageTk.PhotoImage(image))
    return ImageTk.PhotoImage(image)

if __name__ == "__main__":
    root = Tk()
    icon = createIcon('gearIcon.png')

    frame = Frame(root)
    mb = Menubutton(frame, bg='sky blue', image=icon, relief=RIDGE, activebackground='green')
    mb.menu = Menu(mb, tearoff=0)
    # mb.menu.add_command(label="myTest")
    mb.pack(side=LEFT, fill=BOTH)
    # setattr(self, name, mb)
    # parent.add_cascade(menu=mb)
    frame.pack(side=TOP, fill=BOTH)
    m1 = MenuMakerMixin()
    m1.generateMenu(mb, "menu2.xml")
    root.mainloop()
