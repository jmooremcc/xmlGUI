# xmlGUI
This project allows you to use XML files to define a Tkinter GUI

The ExampleFiles folder contains sample xml files and a couple of Python source code files that demonstate
how this xmlGUI library works.

The test1.py can be modified on lines 87 & 88 to use different xml files.
The main2GUI.py file demonstrates a different implementation and use of the library.a

The general idea is to create a class that inherits from GUI_MakerMixin and GUI_Menu_Maker.
You will then add methods that will respond to command and onclick events specified in your xml files.

One xool nice feature of the library is that you can include xml files inside of other xml files.
This makes it possible to reuse GUI definitions in multiple files instead of reinventing the wheel each time.

If you need to access a widget from your code, simply use a name attribute in your xml file.
For example, a button can be named in an xml file like this:
    <button name="delBtn" bg="red" image="gearIcon.png" >
Inside your class, you would access this button widget using self.delBtn.

This is a highly experimental library offered with no guarantees or warranties, so use it at your own risk.

Please look at the GUI_Menu_Maker.pdf file for more information.

