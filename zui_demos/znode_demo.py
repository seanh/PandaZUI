"""Demo of the ZNode class, automatically zooming and panning the camera to 
focus on a ZNode. Use the LMB to zoom in to or pan to a znode, RMB to zoom out again."""

import sys,os,random
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from znode import ZNode
from zcanvas import zcanvas

from pandac.PandaModules import *
import direct.directbase.DirectStart

znode = ZNode(magnification=.9)
znode.reparentTo(zcanvas.home)
znode.set_zoomable(True)
znode.setPos(-.7,0,0)

znode = ZNode(magnification=.7)
znode.reparentTo(zcanvas.home)
znode.set_zoomable(True)
znode.setPos(.7,0,0)

parent = None
for i in range(4):
    znode = ZNode()
    if parent is not None:
        znode.reparentTo(parent.np)
    else:
        znode.reparentTo(zcanvas.home)
    znode.set_zoomable(True)
    znode.setScale(.9)
    znode.setColor(i/3.0,i/3.0,i/3.0,1)        
    parent = znode

base.accept('mouse1',zcanvas.zoomTo)
base.accept('mouse3',zcanvas.zoomToParent)

zcanvas.message('Left-click on a znode to zoom in on it.\n Right-click to zoom out to the parent node or back to home.\n The thing in the middle is four znodes on top of eachother.')

run()