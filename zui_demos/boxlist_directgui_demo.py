"""Demo of boxlists class using different subclasses of BoxList and drag & drop.
"""

import sys,os,random
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import Box
from gridboxlist import GridBoxList
from zcanvas import zcanvas

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.DirectGui import *

gbox = GridBoxList(columns=3,margin=0)
gbox.setPos(-.3,0,.3)
gbox.reparentTo(zcanvas.home)
cm = CardMaker('cm')
cm.setFrame(-.1,.1,-.1,.1)
for i in range(9):
    b = Box(geomnode=cm.generate())    
    gbox.append(b)
    label = DirectButton(text="Hello.")
    label.setScale(0.2)
    b.fill(label)

base.accept('mouse1',zcanvas.drag)
base.accept('mouse1-up',zcanvas.drop)

zcanvas.message(
"""You can put DirectGUI widgets in boxlists too."""
)
            
run()
