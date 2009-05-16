"""Demo for storyMap.py."""

import direct.directbase.DirectStart

import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
sys.path.append(os.path.join(sys.path[0],'../storymaps/'))
from zcanvas import zcanvas
from storyMap import *
from messager import Receiver

class Controller(Receiver):

    def __init__(self):

        m = StoryMap(storyCardClass=FocusableChoosableStoryCard,title="Story Cards")
        m.fill()
        m.setScale(0.02)
        m.setPos(-.5,0,.8)
        m.reparentTo(zcanvas.home)

        n = StoryMap(storyCardClass=FocusableEditableStoryCard,title="My Story")
        n.setScale(0.02)
        n.setPos(-.5,0,-.1)
        n.reparentTo(zcanvas.home)
        n.title['state'] = DGG.NORMAL
                    
controller = Controller()
            
base.accept('mouse2',zcanvas.zoomTo)
base.accept('mouse3',zcanvas.zoomToParent)
base.accept('mouse1',zcanvas.drag)
base.accept('mouse1-up',zcanvas.drop)

zcanvas.message(
"""Drag and drop StoryCards between StoryMaps, and zoom around."""
)

base.setFrameRateMeter(True)

run()
