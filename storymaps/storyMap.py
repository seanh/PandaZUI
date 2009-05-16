import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from zcanvas import zcanvas
from znode import *
from box import Box
from gridboxlist import GridBoxList
from storyCard import *
from functions import Function,functions
from memento import Memento, Originator
from messager import messager,Receiver

from pandac.PandaModules import *
from direct.fsm.FSM import FSM

class StoryMapBox(Box):
   
    def __init__(self, storyCardClass, geomnode=None):
    
        Box.__init__(self, geomnode=geomnode)
        self.storyCardClass = storyCardClass
            
    # StoryMaps work a little differently to normal boxlists. fill() duplicates
    # the given StoryCard, but perhaps using a different StoryCard subclass, and
    # it does not empty the StoryMapBox that the original StoryCard came from,
    # but it informs the StoryMap of that StoryMapBox so that the StoryMap may
    # empty the box, or not, or do something else.
    def fill(self,storyCard):
        if self.contents is not None:
            self._empty()
        # FIXME: StoryCard should have a copy-constructor method, instead of
        # doing all the specifics here in another class.
        newStoryCard = self.storyCardClass(function=storyCard.function)        
        newStoryCard.setPythonTag("box",self)
        newStoryCard.reparentTo(self.np)
        newStoryCard.setColorOff()
        newStoryCard.setPos(VBase3(0,0,0))
        if storyCard.disabled: newStoryCard.disable()
        self.contents = newStoryCard
        self.set_droppable(False)
        if self.boxlist is not None:
            self.boxlist.layout()
        try:
            # Call the `added` method on the StoryMap that the StoryCard
            # original StoryCard belongs to.
            storyCard.getPythonTag('box').getPythonTag('storymap').added(storyCard)
        except AttributeError:
            # The StoryCard does not belong to any StoryMap.
            pass

    # Implement the Originator interface of the Memento pattern (for saving and
    # loading user content.)
    class Memento:
        def __init__(self,contents_memento):
            self.contents_memento = contents_memento
        def __str__(self):        
            if self.contents_memento is not None: return str(self.contents_memento)
            else: return ""

    def create_memento(self):
        if self.contents is None:
            contents_memento = None
        else:
            contents_memento = self.contents.create_memento()
        return StoryMapBox.Memento(contents_memento)
            
    def restore_memento(self,memento):
        if self.contents is not None:
            self.empty()
        if memento.contents_memento is not None:
            card = memento.contents_memento.cls(memento.contents_memento.function)
            card.restore_memento(memento.contents_memento)
            self.fill(card)
            self.contents.entry.enterText(memento.contents_memento.text)
            
class StoryMap(GridBoxList,Receiver):
    """The basic StoryMap class, it is functional on its own and can also be
    subclassed to create custom StoryMap behaviours. A StoryMap is a container
    for StoryCards, it emulates a Python list.

    """

    def __init__(self, storyCardClass, title, num_columns=8):

        self.num_columns = num_columns
        self.storyCardClass = storyCardClass

        # Controls the behaviour of the added method.
        # None : does nothing
        # 'disable' : disables the StoryCard
        # 'remove' : removes the StoryCard from the box.
        self.added_behaviour = None
        
        # Whether or not the StoryMap automatically keeps its StoryCards in the
        # correct order. (StoryCards will be sorted whenever one is added to or
        # removed from the StoryMap.)
        self.keep_sorted = False
            
        GridBoxList.__init__(self,columns=num_columns,margin=1)
        for i in range(len(functions)):
            b = StoryMapBox(storyCardClass, geomnode=card())
            b.setPythonTag('storymap',self)
            self.append(b)
        self.initial_size = len(self)
        self.storyCardClass = storyCardClass
        self.title = DirectEntry(initialText=title,
                                 text_font=loader.loadFont('storymaps/data/WritersFont.ttf'),
                                 width=13,
                                 numLines=1,
                                 suppressMouse=0,
                                 frameColor = (0,0,0,0))
        self.title['state'] = DGG.DISABLED
        self.title.setScale(5)
        self.title.setPos(self.left(),0,self.top())
        self.title.setZ(self.top()+2)        
        self.title.reparentTo(self.np)

        # The add_row_button/remove_row_button is not being used anymore.
        #icon = loader.loadTexture('storymaps/data/actions/remove.svg.png')
        #icon.setMagfilter(Texture.FTLinearMipmapLinear)
        #icon.setMinfilter(Texture.FTLinearMipmapLinear)
        #rollover_icon = loader.loadTexture('storymaps/data/actions/remove_rollover.svg.png')
        #rollover_icon.setMagfilter(Texture.FTLinearMipmapLinear)
        #rollover_icon.setMinfilter(Texture.FTLinearMipmapLinear)        
        #self.remove_row_button = DirectButton(image= (icon, rollover_icon, rollover_icon, icon), command = self.remove_row, suppressMouse=0)
        #self.remove_row_button.reparentTo(self.np)
        #self._position_remove_button()
        #self.remove_row_button.hide()        

        # Task for automatically growing and shrinking the storymap as cards are
        # added and removed.
        self.auto_grow = False
        taskMgr.add(self.add_row_task,'StoryMap.add_row_task')

    # This method not used any more.
    def _position_remove_button(self):
        """Repositions the self.remove_row_button button to the bottom-right of
        the StoryMap."""

        # The boxlist itself is not reporting its bounds correctly for some 
        # reason, so we use the bounds of the last box instead.            
        self.remove_row_button.setPos(self[-1].bottom_right()+Point3(1.5,0,-1.5))
        
        # Reparenting the button to the same parent has the effect of making it
        # the last child node of that node so that it will be drawn last and
        # appear on top of the rest of the StoryMap.
        self.remove_row_button.reparentTo(self.remove_row_button.getParent())

    def add_row_task(self,task):
        """Add a new row of boxes to the bottom of this story map."""
        if not self.auto_grow: return Task.cont        
        if None not in self.items():
            # The StoryMap is full, grow it.
            self.add_row()
        elif self.items()[-self.num_columns:] == \
             [None for i in range(self.num_columns)] and None in \
             self.items()[:-self.num_columns]:
             self.remove_row()
        return Task.cont           
        
    def add_row(self):
        for i in range(self.num_columns):
            b = StoryMapBox(self.storyCardClass, geomnode=card())
            b.setPythonTag('storymap',self)
            self.append(b)      
        #self._position_remove_button()
        #self.remove_row_button.show()
        # FIXME: don't like StoryMap calling zcanvas here, should send some sort
        # of notification instead.
        if zcanvas.focus is None: zcanvas._zoomToNodePath(zcanvas.home)
        
    def remove_row(self):   
        """Remove the last row of boxes from this story map, _if_ all the boxes
        in the row are empty."""
        if len(self) <= self.initial_size:
            return # Don't shrink below initial size
        for item in self.items()[-self.num_columns:]: # The last row.
            if item is not None:
                zcanvas.message('Row is not empty.')
                return
        for box in self.boxes[-self.num_columns:]:
            self.remove(box)
        
    def added(self,card):
        """Callback function, a StoryCard belonging to this StoryMap has been
        duplicated and put in a StoryMapBox somewhere else."""

        if self.added_behaviour is None: return
        else:
            box = card.getPythonTag('box')
            if self.added_behaviour == 'disable':
                box.contents.disable()
            elif self.added_behaviour == 'remove':                        
                box.empty()
                    
    def fill(self):
        # Note that this assumes that len(self) >= len(functions), if it is not
        # an exception will be thrown.
        for index,function in enumerate(functions):
            card = StoryCard(function=function)
            self[index].fill(card)

    def layout(self):
        if self.keep_sorted == True: self.sort()
        GridBoxList.layout(self)

    def _cmp(self,x,y):
        """This is NOT a __cmp__ method for StoryMap, it's a helper method for
        `sort` below. x and y are two StoryMapBox objects, this function
        compares them based on the functions of the StoryCards they contain.
        
        Returns -1 if x<y, 0 if x==y, 1 if x>y."""
        
        if x.contents is None and y.contents is None:
            return 0
        elif x.contents is None:
            return 1
        elif y.contents is None:
            return -1
        else:
            if x.contents.function < y.contents.function: return -1
            elif x.contents.function == y.contents.function: return 0
            elif x.contents.function > y.contents.function: return 1
        raise Exception('Should never reach here! This means StoryMap._cmp is broken.')
        
    def sort(self):
        self.boxes.sort(cmp=self._cmp)

    # Implement the Originator interface of the Memento design pattern for
    # saving and loading user content.
    class Memento(Memento):    
        def __init__(self,title,box_mementos):
            self.title = title
            self.box_mementos = box_mementos            
        def __str__(self):
            string = self.title
            for box_memento in self.box_mementos:
                string += box_memento.__str__()
            return string
              
    def create_memento(self):
        """Return a StoryMapMemento containing a snapshot of this StoryMap's
        current state.
        """
        box_mementos = []
        for box in self:
            box_mementos.append(box.create_memento())
        return StoryMap.Memento(self.title.get(),box_mementos)

    def restore_memento(self,memento):
        """Restore the object's internal state from a memento."""
        self.empty()
        for box_memento in memento.box_mementos:
            box = StoryMapBox(storyCardClass=self.storyCardClass, geomnode=card())
            box.setPythonTag('storymap',self)
            box.restore_memento(box_memento)
            self.append(box)
        self.title.enterText(memento.title)
        self._position_add_button()
        # FIXME: don't like StoryMap calling zcanvas here, should send some sort
        # of notification instead.
        if zcanvas.focus is None: zcanvas._zoomToNodePath(zcanvas.home)        