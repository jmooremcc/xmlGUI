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
from PIL import ImageTk, Image

def GetAttr(parent, fnname):
    nlist = [parent] + fnname.split('.')
    numitems = len(nlist)
    if numitems > 2:
        for n in range(numitems - 1):
            nlist[n+1] = GetAttr(nlist[n],nlist[n+1])

        return nlist[numitems - 1]
    else:
        return getattr(parent,fnname)

def createIcon(imgFilename, size=(32,32)):
    """
    Converts an image into a bitmap that can be used on a menubutton
    :param imgFilename: str
    :return: ImageTk.PhotoImage
    """
    image = Image.open(imgFilename)
    image2 = image.resize(size, Image.ANTIALIAS)
    # setattr(self, iconVarname, ImageTk.PhotoImage(image))
    return ImageTk.PhotoImage(image2)


def calcSize(imgSize, size):
    aspect = imgSize[0] / imgSize[1]  # width/height
    maxDim = max(imgSize[0], imgSize[1])
    if maxDim == imgSize[0]:
        result = size[0], int(size[0] / aspect)
    else:
        result = int(size[0] * aspect), size[0]

    return (result, aspect)

def createPhotoImage(fname, size=(300,300), angle=0, defaultimage=None, noDeleteFlag=False):
    try:
        rotateFlag = False
        if fname != "...":
            image = Image.open(fname)
            # print("calc newSize")
            newSize, aspect = calcSize(image.size, size)
            # print("newSize:{}".format(newSize))
            image.thumbnail(newSize)
            pos = (int((size[0] - newSize[0]) / 2), int((size[1] - newSize[1]) / 2))

    except:
        # self.statusBarMsg("Use placeholder for image")
        if defaultimage is None:
            raise Exception("No image available to load")

        image = Image.open(defaultimage)
        newSize, aspect = calcSize(image.size, size)
        # self.image.thumbnail((250,250))
        # self.image.transform((100,100),Image.AFFINE,data=(1,0,0,2,1,0))
        pos = (0, 0)
        noDeleteFlag = True

    if angle != 0 and fname != None:
        image = image.rotate(angle, expand=True)
        rotateFlag = not rotateFlag
        if rotateFlag:
            pos = (int((size[1] - newSize[1]) / 2), int((size[0] - newSize[0]) / 2))
        else:
            pos = (int((size[0] - newSize[0]) / 2), int((size[1] - newSize[1]) / 2))

    # self.statusBarMsg("Dispaly image")
    # im1 = self.image.resize(newSize)
    im1 = Image.new("RGB", size)

    # print("pos:{}".format(pos))
    im1.paste(image, pos)
    photo = ImageTk.PhotoImage(im1)

    return photo

