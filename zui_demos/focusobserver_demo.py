"""Demo of znode with the focusobserver mixin. Use the LMB to zoom in on and pan to znodes, use the RMB to zoom back again, watch as their colors change. Blue indicates the znode is focused, red indicates the znode's parent is focused, green indicates a sibling of the znode is focused. Also the child znodes, which are positioned inside their parent znodes, do not become zoomable until their parent znodes are focused (you have to zoom to the parent first, you can't just zoom straight to the child)."""

import sys,os,random
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from znode import ZNode,FocusObserver
from zcanvas import zcanvas

from pandac.PandaModules import *
import direct.directbase.DirectStart

class DemoNode(ZNode,FocusObserver):
    """A class that mixes in focusobserver with znode and overrides 
    focusobserver's empty methods to change color in responde to the viewport's 
    focus.
    
    """
    def __init__(self,color):
        ZNode.__init__(self)
        FocusObserver.__init__(self)
        self.color = color
        self.setColor(*color)

    def enterNone(self):
        """Viewport focus has changed to None."""
        pass
    def exitNone(self):
        """Undo any changes made by enterNone."""
        pass

    def enterSelf(self):
        """Viewport focus has changed to this znode."""
        self.setColor(0,0,1,1)
    def exitSelf(self):
        """Undo any changes made by enterSelf."""
        self.setColor(*self.color)

    def enterParent(self):
        """Viewport focus has changed to the lowest zoomable ancestor node of
        this znode."""
        self.setColor(1,0,0,1)
    def exitParent(self):
        """Undo any changes made by enterParent."""
        self.setColor(*self.color)
        
    def enterSibling(self):
        """Viewport focus has changed to a sibling znode of this znode."""
        self.setColor(0,1,0,1)
    def exitSibling(self):
        """Undo any changes made by enterSibling."""
        self.setColor(*self.color)

    def enterOther(self):
        """Viewport focus has changed to some other znode."""
        pass
    def exitOther(self):
        """Undo any changes made by enterOther."""
        pass

class ChildNode(DemoNode):
    """A node automatically becomes zoomable when its parent node is focused,
    as well as changing color like DemoNode."""

    def __init__(self,color):
        DemoNode.__init__(self,color)

    def enterParent(self):
        """Viewport focus has changed to the lowest zoomable ancestor node of
        this znode."""
        DemoNode.enterParent(self)
        self.set_zoomable(True)
    def exitParent(self):
        """Undo any changes made by enterParent."""
        DemoNode.exitParent(self)
        self.set_zoomable(False)

nodes = []    
for x in (-1,-.5,0,.5,1):
    node = DemoNode(color=(1,1,1,1))
    node.reparentTo(zcanvas.home)
    node.set_zoomable(True)
    node.setPos(x,0,0)
    node.setScale(.7)
    nodes.append(node)
    
for node in nodes:
    childnode = ChildNode(color=(0,0,0,0))
    childnode.reparentTo(node.np)
    childnode.setScale(.33)
    
base.accept('mouse1',zcanvas.zoomTo)
base.accept('mouse3',zcanvas.zoomToParent)

zcanvas.message('Left click on something to focus it (zoom in on it).\nRight-click to zoom back out.\nObjects change color depending on whether you are focused on\nthem (blue), their parent element (red),\none of their sibling elements (green), or nothing (white or black).',duration=10)
    
run()