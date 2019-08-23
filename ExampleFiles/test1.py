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
import os
from TkinterInterface import *
from GUI_MakerMixin import *
from GUI_MakerMixin import GUI_MakerMixin
from MenuMakerMixin import MenuMakerMixin

class Test(GUI_MakerMixin, MenuMakerMixin):
    def __init__(self, topLevelWindow=None, outputfilename=None):
        GUI_MakerMixin.__init__(self, topLevelWindow=topLevelWindow, outputfilename=outputfilename)
        MenuMakerMixin.__init__(self, topLevelWidget=topLevelWindow)

    def demoProc(self, *arg):
        myarg = arg[0]
        if 'demo'in myarg.lower():
            val = self.v1.get()
            print("Demo called: {}:{}".format(myarg, val))



    def noop(self, *arg):
        """
        Sample onclick handler
        :param arg:
        :return:
        """
        if len(arg) == 1:
            if type(arg) == tuple:
                try:
                    myarg = GetAttr(self, arg[0])
                except:
                    myarg = arg[0]

                try:
                    if isinstance(myarg, StringVarPlus) or isinstance(myarg, mGraphicsLibName.IntVar):
                        # myarg = myarg.get()
                        print("noop called: {}:{}".format(arg[0], myarg.get()))
                        return
                    else:
                        print("arg: {}".format(arg))
                except:
                    print("arg: {}".format(arg))
            else:
                myarg = arg
        elif len(arg) == 0:
            print("arg: {}".format(arg))
        else:
            myarg = arg[0]
            print("noop called: {}:{}:{}".format(myarg, arg[1], GetAttr(self, myarg).get()))





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



root = mRootWindow()
root.geometry("330x360")
os.chdir(r"D:\My Documents\GitHub\xmlGUI\ExampleFiles")
m1 = Test(root)
m1.makeGUI(root, "gui6.xml")
m1.generateMenu("testmenu.xml", root)
root.mainloop()