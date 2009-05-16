"""Demo of boxlists class using different subclasses of BoxList and drag & drop.
"""

import sys,os,random
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from znode import ZNode,Draggable,Highlightable
from box import Box
from hboxlist import HBoxList
from vboxlist import VBoxList
from gridboxlist import GridBoxList
from zcanvas import zcanvas

from pandac.PandaModules import *
import direct.directbase.DirectStart

class DemoItem(ZNode,Draggable,Highlightable):
    """A draggable zode with some geometry from cardmaker."""

    cm = CardMaker('cm')
    cm.setFrame(-.1,.1,-.1,.1)

    def __init__(self):
    
        ZNode.__init__(self,geomnode = DemoItem.cm.generate())
        Draggable.__init__(self)
        self.set_draggable(True)
        Highlightable.__init__(self)
        self.set_highlightable(True)
        # FIXME. zoomable is required to make highlightable work because of the
        # collision mask. It shouldn't be.
        self.set_zoomable(True)

hbox = HBoxList()
hbox.setPos(-.5,0,.4)
hbox.reparentTo(zcanvas.home)
for i in range(5):
    b = Box(geomnode=DemoItem.cm.generate())    
    hbox.append(b)
    i = DemoItem()
    b.fill(i)

vbox = VBoxList()
vbox.setPos(-.5,0,.25)
vbox.reparentTo(zcanvas.home)
for i in range(5):
    b = Box(geomnode=DemoItem.cm.generate())    
    vbox.append(b)

gbox = GridBoxList(columns=3)
gbox.setPos(.1,0,.1)
gbox.reparentTo(zcanvas.home)
for i in range(9):
    b = Box(geomnode=DemoItem.cm.generate())    
    gbox.append(b)

base.accept('mouse1',zcanvas.drag)
base.accept('mouse1-up',zcanvas.drop)

zcanvas.message(
"""Drag the demo items (in white) and
drop them onto the boxes (in black)."""
)
            
run()
