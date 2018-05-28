#
def GetAttr(parent, fnname):
    nlist = [parent] + fnname.split('.')
    numitems = len(nlist)
    if numitems > 2:
        for n in range(numitems - 1):
            nlist[n+1] = GetAttr(nlist[n],nlist[n+1])

        return nlist[numitems - 1]
    else:
        return getattr(parent,fnname)
