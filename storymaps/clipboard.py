"""Contains the global singleton clipboard object instance `clipboard`."""

# I'm not actually using this module yet, EditableStoryCard just uses a class
# variable instead to implement a simple clipboard. But if clipboard
# functionality were to be extended beyond that class this singleton would be
# the way to go.


class Clipboard:
    """A global singleton clipboard object that subscribes to the copy and paste 
    signals and implements copy and paste in response. Maintains a list of the
    last 10 copied items. When an item is pasted it is removed from the list.
    Can be accessed like a Python list: clipboard[-1] is the most recently
    copied item, clipboard[0] the oldest. Accessing items in this way does not
    remove them from the clipboard.
    
    """
    def __init__(self):
    
        self._items = []
        self.limit = 10
        messager.accept('copy',self.copy)
        messager.accept('paste',self.paste)
        
    def copy(self,accepterArg,text):
    
        self._items.append(text)
        if len(self) > 10: self._items.pop(0)
        
    def paste(self,accepterArg,func):
    
        func(self._items.pop())
         
    def __len__(self):
        return len(self._items) 

    def __getitem__(self,key):
        return self._items[key]

    def __contains__(self,item):
        return (item in self._items)

clipboard = Clipboard()