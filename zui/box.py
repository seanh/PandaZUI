""" 
box.py -- some nodepath-like objects meant to contain other nodepath-like
objects and position and align them in lines or grids.

"""

from pandac.PandaModules import *
from direct.gui.DirectGui import *
from znode import ZNode,Droppable,NodePathWrapper
from zcanvas import zcanvas
        
class BoxAlreadyEmptyError(Exception):
    """An attempt was made to empty a box when it was already empty."""
    pass

# FIXME: better support for customising the highlighting. Perhaps it should be
# possible to pass two geomnodes, the unhighlighted one and the highlighted one.
# (But this is for class Highlightable, not Box).
class Box(ZNode,Droppable):
    """A box that can hold one or zero items a a time, and that supports being
    dropped onto when not already holding an item."""

    def __init__(self,geomnode=None):

        if geomnode is None:         
            scale = 0.024
            left,right,bottom,top = -3*scale,3*scale,-4*scale,4*scale
            cm = CardMaker('Box')            
            cm.setFrame(left,right,bottom,top)
            geomnode = cm.generate()
            
        ZNode.__init__(self,geomnode=geomnode,magnification=.8)
        Droppable.__init__(self)
        self.set_droppable(True)

        # Enable transparency and make the box invisible.
        self.np.setTransparency(TransparencyAttrib.MAlpha)
        self.np.setColor(.3,.3,.3,1)
        #self.np.setScale(scale)

        # Uncomment to apply a texture to the object.
        #tex = loader.loadTexture('card.png')
        #self.np.setTexture(tex)
        
        # The nodepath currently held by this box.
        self.contents = None
        
        # The boxlist that this box currently belongs to.
        self.boxlist = None       
        
    def drop(self,event):
        Droppable.drop(self,event)
        self.fill(event.draggable)

    def _empty(self):
        """Helper method for fill and empty."""

        if self.contents is None:
            raise BoxAlreadyEmptyError()
        else:
            self.contents.detachNode()
            self.contents.clearPythonTag("box")
            self.contents = None
            self.set_droppable(True)

    def fill(self,item):
        """Place an item into this box. Any item already in this box will be
        replaced."""

        if self.contents is not None:
            self._empty()
        if item.getPythonTag("box") is not None:
            item.getPythonTag("box").empty()
        item.setPythonTag("box",self)
        item.reparentTo(self.np)
        item.setColorOff()
        item.setPos(VBase3(0,0,0))
        self.contents = item
        self.set_droppable(False)
        if self.boxlist is not None:
            self.boxlist.layout()

    def empty(self):
        """Empty any nodepath from this box. An exception will be thrown if this
        box is already empty."""

        self._empty()
        if self.boxlist is not None:
            self.boxlist.layout()

    def __str__(self):
        return 'Box holding '+str(self.contents)

    # Make Box DGUI compatible.
    # (getTightBounds() always returns 0 for DirectGUI nodepaths, and therefore
    # they contribure nothing to the bounds of their parent node, so if the
    # contents of a box is a DirectGUI object we need to make a special case
    # when computing the bounds of the box.)
    # This involves a not-very-pythonic type check, but it works.
    def isDGUI(self,obj):
        tmpNP = NodePath('temp')
        PGfound = not obj.instanceUnderNode(tmpNP,'').find('+PGItem').isEmpty()
        tmpNP.removeNode()
        return PGfound                  
    
    def bottom_left(self):
        if self.contents is not None and self.isDGUI(self.contents):
            bounds = self.contents.node().getFrame()
            l,r,b,t = bounds.getX(),bounds.getY(),bounds.getZ(),bounds.getW()
            bottom_left = Point3(l,0,b)
            bottom_left = self.getParent().getRelativePoint(self.contents,bottom_left)
        else: 
            bottom_left = self.np.getTightBounds()[0]
        return bottom_left        
    
    def top_right(self):
        if self.contents is not None and self.isDGUI(self.contents):
            bounds = self.contents.node().getFrame()
            l,r,b,t = bounds.getX(),bounds.getY(),bounds.getZ(),bounds.getW()

            top_right = Point3(r,0,t)
            top_right = self.getParent().getRelativePoint(self.contents,top_right)
        else:
            top_right = self.np.getTightBounds()[1]
        return top_right
    
    def getTightBounds(self):
        return (self.bottom_left(),self.top_right())