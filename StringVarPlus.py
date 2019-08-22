#StringVarPlus.py
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
# from Tkinter import *
try:
    from Tkinter import *
    import Tkconstants
except ImportError:
    from tkinter import *
    import tkinter.constants
    Tkconstants = tkinter.constants

class StringVarPlus(StringVar):
    # def __new__(cls, name):
    #     return StringVar.__new__(cls)

    def __init__(self):
        StringVar.__init__(self)
        self.name=""

    @property
    def Name(self):
        return self.name

    @Name.setter
    def Name(self, value):
        self.name = value

    def __repr__(self):
        return "%s:%s" % (self.Name,self.get())
