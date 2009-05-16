"""Demo for storyCard.py."""
import direct.directbase.DirectStart

import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
sys.path.append(os.path.join(sys.path[0],'../storymaps/'))
from zcanvas import zcanvas
from storyCard import *
from functions import functions
from messager import Receiver

class Controller(Receiver):

    def __init__(self):

        self.storycards = []
        for i in range(6):
            if i in (0,2,4,6):
                s = FocusableChoosableStoryCard(function = functions[i])
            else:
                s = FocusableEditableStoryCard(function = functions[i])
            s.set_zoomable(True)
            s.set_draggable(True)
            s.set_highlightable(True)
            s.set_detail("low")
            s.show_buttons(False)
            s.set_editable(False)
            s.setScale(0.06)
            s.setPos((i%3)*0.4-.5,0,-(i/3)*0.5+.25)
            s.reparentTo(zcanvas.home)
            self.storycards.append(s)

        self.acceptOnce('zoom done',zcanvas.message,'Right-click to zoom back out again.')
        self.accept('add',self.add)
        self.accept('remove',self.remove)
        
    def add(self,card):
        zcanvas.message('Add button was pressed on card "'+card.function.name+'"')

    def remove(self,card):
        zcanvas.message('Remove button was pressed on card "'+card.function.name+'"')


                    
controller = Controller()
            
base.accept('mouse1',zcanvas.zoomTo)
base.accept('mouse3',zcanvas.zoomToParent)
base.accept('mouse2',zcanvas.drag)
base.accept('mouse2-up',zcanvas.drop)

zcanvas.message(
"""Mouse-over to highlight a StoryCard,
left-click to focus (zoom in on) it,
middle-click to drag it."""
)

run()
