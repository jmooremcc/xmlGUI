#
import Tkinter

class TkinterInterface(object):
    def GetAttr(self, object, name, default=None):
        getattr(object, name, default=default)


