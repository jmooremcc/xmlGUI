#StringVarPlus.py

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
