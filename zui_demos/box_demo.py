"""A demo of box.py, drag & drop items (in white) between boxes (in black), with
mouse-over highlighting."""

import sys,os,random
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from znode import ZNode,Draggable,Highlightable
from box import Box
from zcanvas import zcanvas

from pandac.PandaModules import *
import direct.directbase.DirectStart

class DemoItem(ZNode,Draggable,Highlightable):
    """A draggable zode with some geometry from cardmaker."""

    cm = CardMaker('cm')
    cm.setFrame(-.2,.2,-.2,.2)

    def __init__(self):
    
        ZNode.__init__(self,geomnode = DemoItem.cm.generate())
        # FIXME. Currently highlightable only works when zoomable.
        self.set_zoomable(True)
        Highlightable.__init__(self)
        self.set_highlightable(True)
        Draggable.__init__(self)
        self.set_draggable(True)

for i in range(5):
    b = Box(geomnode=DemoItem.cm.generate())
    b.setPos(i*0.5-1,0,0.5)
    b.reparentTo(zcanvas.home)
    d = DemoItem()
    d.setPos(i*0.5-1,0,-0.5)
    d.reparentTo(zcanvas.home)            
                
base.accept('mouse1',zcanvas.drag)
base.accept('mouse1-up',zcanvas.drop)

zcanvas.message(
"""Drag the demo items (in white) and
drop them onto the boxes (in black)."""
)
            
run()
