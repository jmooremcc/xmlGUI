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

