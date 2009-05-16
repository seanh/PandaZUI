import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import Box
from vboxlist import VBoxList
from memento import Memento, Originator
from storyCard import card, StoryCard
from storyMap import StoryMapBox

from pandac.PandaModules import *

# TODO: implement the background geometry and sliding in and out into this class.

# FIXME: Stack implements the same interface as StoryMap but using a VBoxList
# instead of an HBoxList. Stack and StoryMap should be refactored so they can
# share code.
class Stack(VBoxList):

    def __init__(self):
    
        VBoxList.__init__(self,margin=1.5)
        for i in range(10):
            b = StoryMapBox(storyCardClass=StoryCard,geomnode=card())
            b.setPythonTag('storymap',self)
            self.append(b)

        self.right_np = aspect2d.attachNewNode('right frame')
        width = 0.2*base.getAspectRatio()
        self.right_np.setPos(base.getAspectRatio()+width,0,1)

    def added(self,card):
        """Callback function, a StoryCard belonging to this StoryMap has been
        duplicated and put in a StoryMapBox somewhere else."""

        box = card.getPythonTag('box')
        box.empty()

    def layout(self):
        VBoxList.layout(self)
        cards = [item for item in self.items() if item is not None]
        for card in cards:
            card.set_draggable(True)
            
    # Implement the Originator interface of the Memento design pattern for
    # saving and loading user content.
    class Memento(Memento):    
        def __init__(self,box_mementos):
            self.box_mementos = box_mementos            
        def __str__(self):            
            s = ""
            for box_memento in self.box_mementos:
                s += box_memento.__str__()
            return 'Stack containing '+s
              
    def create_memento(self):
        box_mementos = []
        for box in self:
            box_mementos.append(box.create_memento())
        return Stack.Memento(box_mementos)

    def restore_memento(self,memento):
        self.empty()
        for box_memento in memento.box_mementos:
            box = StoryMapBox(storyCardClass=StoryCard,geomnode=card())
            box.setPythonTag('storymap',self)
            box.restore_memento(box_memento)
            self.append(box)