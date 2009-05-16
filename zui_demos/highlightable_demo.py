"""Demo of znode with the highlightable mixin. Mouse-over the znodes to see them highlight and unhighlight."""

import sys,os,random
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from znode import ZNode,Highlightable
from zcanvas import zcanvas

from pandac.PandaModules import *
import direct.directbase.DirectStart

class DemoNode(ZNode,Highlightable):
    """A class that just mixes in highlightable with znode."""
    def __init__(self):
        ZNode.__init__(self)
        Highlightable.__init__(self)

for x in (-1,-.5,0,.5,1):
    node = DemoNode()
    node.reparentTo(zcanvas.home)
    node.set_highlightable(True)
    node.setPos(x,0,0)
    node.setScale(.7)

zcanvas.message('Move the mouse cursor over the items and watch them highlight.')
    
run()
