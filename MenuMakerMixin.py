#MenuMakerMixin

import xml.etree.ElementTree as ET
from Tkinter import *
from functools import partial

"""
<menus>
    <menu name='' type=''>
        <menuitem name='' onclick='' />
    </menu>
    <optionmenu name='' id='' default=''/>
         <radioitem name='' value='' onclick='' default=''/>
        .
        .
        .
</menus>
"""

class MenuMakerMixin(object):
    def __init__(self, parent, xmlfile):
        tree = ET.parse(xmlfile)
        self.root = tree.getroot()
        if self.root.tag != 'menus':
            raise Exception("%s does not containthe required menus tag" % xmlfile)

        self.menuItems={}
        menu = Menu(parent)
        self.parseMenuTree(menu,self.root)
        parent.config(menu=menu)

    def processChildElement(self, newMenu, child, radiobuttonoptvar=None):
            menuItemName = child.attrib['name']
            kwargs = {}
            kwargs['label'] = menuItemName

            if radiobuttonoptvar == None:
                shortcut = None
                if 'shortcut' in child.attrib:
                    shortcut = child.attrib['shortcut']
                    kwargs['accelerator'] = shortcut
                    kwargs['underline'] = 0

                if 'onclick' in child.attrib:
                    onclickCallbackName = child.attrib['onclick']
                    kwargs['command'] = partial(self.__getattribute__(onclickCallbackName), menuItemName)

                newMenu.add_command(**kwargs)

            else:
                optvar=radiobuttonoptvar
                kwargs['variable'] = optvar
                kwargs['value'] = child.attrib['value']

                if 'onclick' in child.attrib:
                    callback = child.attrib['onclick']
                    kwargs['command'] = partial(self.__getattribute__(callback), kwargs['value'])

                newMenu.add_radiobutton(**kwargs)

                if 'default' in child.attrib:
                    optvar.set(kwargs['value'])




    def parseMenuTree(self, parent, elem):
        if elem.tag == 'menu':
            print("menu: %s " % elem.tag)
            menuName = elem.attrib['name']
            newMenu = Menu(parent, tearoff=0)
            parent.add_cascade(label=menuName, menu=newMenu)
            print("menuName: %s" % menuName)
            if 'type' in elem.attrib:
                menuType = elem.attrib[type]
                print("menu type is %s" % menuType)
            else:
                pass

            for child in elem:
                if child.tag == 'menu':
                    self.parseMenuTree(newMenu, child)
                elif child.tag == 'separator':
                    newMenu.add_separator()
                elif child.tag == 'optionmenu':
                    id=child.attrib['id']
                    optmenu = Menu(parent, tearoff=0)
                    newMenu.add_cascade(label=child.attrib['name'], menu=optmenu)
                    setattr(self,id,optmenu)
                    if len(child.items()) == 0:
                        self.fillOptionValues(newMenu,self.noop)
                    else:
                        optvar = StringVar()
                        setattr(self,id+'Var',optvar)
                        for childopt in child:
                            self.processChildElement(optmenu,childopt,radiobuttonoptvar=optvar)
                else:
                    self.processChildElement(newMenu, child)

        elif elem.tag == 'menus':
            for child in elem:
                if child.tag == 'menuitem':
                    self.processChildElement(parent, child)
                else:
                    self.parseMenuTree(parent, child)
        else:
           raise Exception("tag: %s is not a menu tag" % elem.tag)
           #  self.processChildElement(parent, elem)

    def fillOptionValues(self, optmenu, callback):
        values=['OE2','OE3','LocalHost']
        optvar = StringVar()

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

if __name__ == "__main__":
    root = Tk()
    m1 = MenuMakerMixin(root, "menu.xml")
    root.mainloop()
