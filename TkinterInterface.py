#
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
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

from functools import partial


def mFrame(master, *args, **kwargs):
    return Frame(master, *args, **kwargs)



# def mSetAttr(p_object, name, value):
#     return setattr(p_object, name, value)

def mRootWindow():
    return Tk()



def getTkinter():
    try:
        import tkinter
        return tkinter
    except:
        import Tkinter
        return Tkinter

mGraphicsLibName = getTkinter()

def mPartial( func, *args, **keywords):
    return partial( func, *args, **keywords)

