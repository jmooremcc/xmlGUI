#
import Tkinter
from functools import partial


# def mGetAttr(object, name):
#     return getattr(object, name)


def mFrame(master, *args, **kwargs):
    return Tkinter.Frame(master, *args, **kwargs)

# def mSetAttr(p_object, name, value):
#     return setattr(p_object, name, value)

def mRootWindow():
    return Tkinter.Tk()

mGraphicsLibName = Tkinter

def mPartial( func, *args, **keywords):
    return partial( func, *args, **keywords)

