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
from tkinter import messagebox
from tkinter.constants import *
import tkinter as tk
import clipboard
import os, os.path
import xml.etree.ElementTree as ET
# from ProgressDialog import ProgressDialog
from time import sleep
from GUI_MakerMixin import GUI_MakerMixin
from MenuMakerMixin import MenuMakerMixin

DEFAULT_DIR = r"D:\Downloads"
HOME_DIR = ""
APP_TITLE = "Test Python App"
SETTINGS_FILE = './settings.xml'
DEFAULT_DIR_Template = "Default Music Directory: {}"
AUTO_DELETE_MODE_Template = "Auto URL Delete Mode: {}"
PERCENTAGE_PER_FILE = 0
Downloadpct = 0
__VERSION__ = 1.0
HELPTEXT = APP_TITLE + "\nVersion {}".format(__VERSION__) + "\n© Copyright 2019\nby John Moore"



class GUI(GUI_MakerMixin,MenuMakerMixin):
    def __init__(self):
        root = self.root = tk.Tk()
        self.toplevel = self.root.winfo_toplevel()
        self.root.title(APP_TITLE)
        self.root.minsize(400, 400)
        self.root.resizable(0, 0)
        self.root.protocol('WM_DELETE_WINDOW', self.onExit)  # root is your root window
        frame = tk.Frame(root, bd=2)
        MenuMakerMixin.__init__(self, frame)
        GUI_MakerMixin.__init__(self, frame)
        self.makeGUI(frame,"mainGUI.xml")
        self.generateMenu("mainGUImenu.xml", root)

        self.defaultDirLabel.set(DEFAULT_DIR_Template.format(r"D:\Music"))
        self.autoDelModeLbl.set(AUTO_DELETE_MODE_Template.format("OFF"))

        frame.pack(side=TOP, fill=BOTH)
        self.root.mainloop()

    def onExit(self):
        exit()

    def deleteOp(self):
        print("Delete Operation Called")

    def clearAllOp(self):
        print("Clear All Operation Called")
        self.downloadBtn.configure(state=DISABLED)

    def pasteOp(self):
        print("Paste Operation Called")
        self.downloadBtn.configure(state=NORMAL)

    def processDirectoryOp(self):
        print("Process Directory Operation Called")

    def downloadProcessor(self, output, proc):
        print("Download Processor Called")

    def activateProgressDialog(self):
        pass

    def downloadOp(self):
        print("Download Operation Called")

    def musicPathSettingsOp(self):
        print("Music Path Settings Called")

    def autoDeleteSettingsOp(self):
        print("Auto Delete Settings Operation Called")

    def autoDownloadArtOp(self):
        print("Auto Download Art Option")

    def helpmenuOp(self):
        messagebox.showinfo(APP_TITLE,HELPTEXT)


if __name__ == "__main__":
    HOME_DIR = os.path.abspath(os.curdir)
    print("Home Dir: {}".format(HOME_DIR))
    app = GUI()