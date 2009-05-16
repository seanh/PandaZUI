from box import Box
from znode import NodePathWrapper

class BoxList(object,NodePathWrapper):
    """An ordered list of Box objects, base class for classes that control the
    layout of lists of boxes.
    
    Unlike putting objects into a normal python list, putting a box object into
    a boxlist has side effects: the box's nodepath will be reparented to the
    boxlist's nodepath in the scene graph, the box's boxlist attritube will be
    set to the boxlist, and the box will be removed from any boxlist that it was
    previously contained in (a box can only be in one boxlist at a time, and
    one boxlist can only contain the same box once).
    
    This class is not much use by itself, but it is meant as the base class for
    classes that want to implement layouts for lists of boxes. The method
    `layout` is called whenever the list of boxes changes, by default the method
    does nothing, subclasses should override it to implement layouts by
    positioning the boxes of the list into some formation.
        
    The individual boxes of a boxlist can be accessed using [] notation:
    
        box = boxlist[offset]
        
    To fill a box that is already in a boxlist with an item:
    
        boxlist[offset].fill(item)
        
    To empty a box (but leave the empty box in the boxlist):
    
        boxlist[offset].empty()
        
    As well as filling and emptying boxes that are already in a boxlist, boxes
    themselves can be added to and removed from a boxlist (and this is necessary
    because initially a boxlist is an empty list, it contains no boxes). To add
    a new box (empty or full) to a boxlist:
    
        boxlist.append(box)
            
    To insert a box:
    
        boxlist.insert(offset,box)

    To replace a box with another box:
    
        boxlist[offset] = box
        
    To add a sequence of boxes to a boxlist:
    
        boxlist.extend(sequence)
        
    To remove a box from a boxlist:
    
        del boxlist[offset]    
    
    Also
    
        boxlist.pop()
        
    removes and returns the last box in the boxlist,
    
        boxlist.pop(offset)
        
    removes and returns the box at `offset` in the boxlist.
            
    To sort a boxlist:
    
        boxlist.sort([func [, key [, reverse]]])

    Parts of BoxList rely on object identity being used to compare Box objects
    (Box defines no __cmp__ method), I am not sure what would happen if a Box
    subclass that defines a __cmp__ were used. To sort a boxlist based on, e.g.,
    the contents of the boxes, better to pass a cmp method to sort instead.
        
    To reverse a boxlist:
    
        boxlist.reverse()
        
    To search a boxlist:
    
        boxlist.index(box)
        
    returns the index of `box` in the boxlist. Raises ValueError if `box` is not
    in the boxlist.
        
        boxlist.remove(box)

    deletes `box` from the boxlist, raises ValueError if `box` is not in the
    boxlist.
    
    You can also get an ordered list of all the Item objects containd by all the
    Box objects in a BoxList:
    
        items = boxlist.items()
        
    The list of items will contain None for each empty box in the boxlist.
                    
    """    
    def __init__(self):
            
        # A boxlist is itself a nodepath-like object and parents all of its
        # boxes to its nodepath self.np in the scene graph.
        NodePathWrapper.__init__(self)

        # The list of Boxes belonging to boxlist.
        self.boxes = []

    # User methods for accessing the list.
    def __len__(self):
        """Return the length of this boxlist."""
        return len(self.boxes)
        
    def __getitem__(self,offset):
        """Return the box at `offset` in this boxlist."""
        return self.boxes[offset]

    def __contains__(self,box):
        """Return True if `box` is in this boxlist, False otherwise."""
        return (box in self.boxes)

    def index(self,box):
        """Return the index (offset) of `box` in this boxlist.
        """
        return self.boxes.index(box)

    def items(self):
        """Return a list of all the items contained in all the boxes owned by
        this boxlist. The list of items will contain a None value for each empty
        box in this boxlist."""
        items = []
        for box in self.boxes:
            items.append(box.contents)
        return items

    # A few helper methods that do some of the real work.
    def _del(self,offset):
        """Helper method for setitem and delitem."""
        box = self[offset]
        box.boxlist = None
        box.detachNode()
        del self.boxes[offset]

    def _update(self,box):
        """Helper method for helper methods _insert and _add."""
        if box.boxlist is not None:
            box.boxlist.remove(box)
        box.boxlist = self
        box.reparentTo(self.np)

    def _insert(self,offset,box):
        """Helper method for setitem and insert."""
        self.boxes.insert(offset,box)
        self._update(box)

    def _add(self,box):
        """Helper method for append and extend."""
        self.boxes.append(box)
        self._update(box)

    # User methods for modifying the list.
    def __setitem__(self,offset,box):
        """Replace the box at `offset` in this boxlist with `box`."""
        self._del(offset)
        self._insert(offset,box)        
        self.layout()

    def __delitem__(self,offset):
        """Remove the box at `offset` from this boxlist."""
        self._del(offset)
        self.layout()
        
    def append(self,box):
        """Append `box` to this boxlist."""
        self._add(box)
        self.layout()
        
    def extend(self,sequence):
        """Append each box in `sequence` to this boxlist in turn."""
        for box in sequence:
            self._add(box)
        self.layout()

    def insert(self,offset,box):
        """Insert `box` at `offset` in this boxlist."""
        self._insert(offset,box)
        self.layout()

    def remove(self,box):
        """Remove `box` from this boxlist."""
        offset = self.index(box)
        del self[offset]

    def pop(self,offset=-1):
        """Remove and return the box at `offset` in this boxlist."""
        box = self[offset]
        del self[offset]
        return box

    def reverse(self,*args):
        """Reverse the order of the boxes in this boxlist."""
        self.boxes.reverse(*args)
        self.layout()
        
    def sort(self,*args):
        """Sort the boxes in this boxlist."""
        self.boxes.sort(*args)
        self.layout()
        
    def layout(self):
        """Reposition all of the boxes in this boxlist to achieve the desired 
        layout. This method is called whenever a box is added or removed from
        the list, or the contents of a box in the list change. Subclasses should 
        override this method to implement layouts.
        """
        pass
        
    def empty(self):
        """Remove all boxes from this boxlist."""

        while len(self) > 0:        
            self.remove(self[0])