import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from zcanvas import zcanvas
from storyMap import *
from messager import messager, Receiver
from memento import Memento, Originator, Caretaker
from hboxlist import HBoxList
from stack import Stack

from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *

from xml.dom import minidom
import cPickle

class Mediator(Receiver,FocusObserver,NodePathWrapper):
    """The singleton mediatorobject mediates the interaction between the
    StoryMap objects, receiving notifications and calling methods on StoryMap
    objects.

    """
    def __init__(self):

        # Create two story maps, 'Story Cards' which the user picks story cards
        # from, and 'My Story Map' in which the user constructs her story.
        self.storyCards = StoryMap(storyCardClass=FocusableChoosableStoryCard, 
                                   title="Story Cards")
        self.storyCards.reparentTo(zcanvas.home)
        self.storyCards.setScale(0.02)
        self.storyCards.setPos(-.5,0,.8)
        self.storyCards.fill()
        self.storyCards.added_behaviour = 'disable'
        
        self.myStoryMap = StoryMap(storyCardClass=FocusableEditableStoryCard, 
                                   title="My Story")
        self.myStoryMap.reparentTo(zcanvas.home)
        self.myStoryMap.setScale(0.02)
        self.myStoryMap.setPos(-.5,0,-.1)
        self.myStoryMap.added_behaviour = 'remove'
        #self.myStoryMap.keep_sorted = True        
        #self.myStoryMap.np.showTightBounds()
        self.myStoryMap.auto_grow = True
               
        # Keyboard controls for saving, loading and exporting.
        #base.accept("f1",self.save)
        #base.accept("f2",self.load)
        #base.accept("f3",self.export)
        
        # Subscribe to some messages.
        self.acceptOnce('zoom done',zcanvas.message,["Right-click to zoom back out again."])
        self.accept('add',self.add)
        self.accept('remove',self.remove)

        # Frame along the bottom for Save, Load and Quit buttons.
        self.bottom_np = aspect2d.attachNewNode('bottom frame')
        height = 0.15
        self.bottom_np.setPos(-base.getAspectRatio(),0,-1-height)
        cm = CardMaker('bottom frame')
        cm.setFrame(0,2*base.getAspectRatio(),0,height)
        self.bottom_np.attachNewNode(cm.generate())
        self.bottom_np.setTransparency(TransparencyAttrib.MAlpha)
        self.bottom_np.setColor(.1,.1,.1,.7)
        self.bottom_hbox = HBoxList(margin=1)
        self.bottom_hbox.reparentTo(self.bottom_np)
        self.bottom_hbox.setPos(0,0,height-0.03)
        self.bottom_hbox.setScale(.1)    
        self.save_button = DirectButton(text="Save",command=self.save)
        b = Box()
        b.fill(self.save_button)
        self.bottom_hbox.append(b)
        self.load_button = DirectButton(text="Load",command=self.load)
        b = Box()
        b.fill(self.load_button)
        self.bottom_hbox.append(b)
        # Interval that slides the frame onto the screen.
        self.bottom_interval = LerpPosInterval(
                            self.bottom_np,
                            duration=1,
                            pos=Point3(-base.getAspectRatio(),0,-1),
                            startPos=Point3(-base.getAspectRatio(),0,-1-height),
                            other=None,
                            blendType='easeInOut',
                            bakeInStart=1,
                            fluid=0,
                            name=None)
        self.bottom_reverse_interval = LerpPosInterval(
                                 self.bottom_np,
                                 duration=1,
                                 pos=Point3(-base.getAspectRatio(),0,-1-height),
                                 startPos=Point3(-base.getAspectRatio(),0,-1),
                                 other=None,
                                 blendType='easeInOut',
                                 bakeInStart=1,
                                 fluid=0,
                                 name=None)
        self.bottom_frame_is_active = False

        # Frame along the right for story cards.
        self.right_np = aspect2d.attachNewNode('right frame')
        width = 0.14*base.getAspectRatio()
        self.right_np.setPos(base.getAspectRatio()+width,0,1)
        cm = CardMaker('right frame')
        cm.setFrame(-width,0,-2,0)
        self.right_np.attachNewNode(cm.generate())
        self.right_np.setTransparency(TransparencyAttrib.MAlpha)
        self.right_np.setColor(.1,.1,.1,.7)
        self.right_vbox = Stack()
        self.right_vbox.reparentTo(self.right_np)
        self.right_vbox.setPos(-width+0.035,0,-0.06)
        self.right_vbox.setScale(.02)
        # Interval that slides the frame onto the screen.
        self.right_interval = LerpPosInterval(
                               self.right_np,
                               duration=1,
                               pos=Point3(base.getAspectRatio(),0,1),
                               startPos=Point3(base.getAspectRatio()+width,0,1),
                               other=None,
                               blendType='easeInOut',
                               bakeInStart=1,
                               fluid=0,
                               name=None)
        self.right_reverse_interval = LerpPosInterval(
                                    self.right_np,
                                    duration=1,
                                    pos=Point3(base.getAspectRatio()+width,0,1),
                                    startPos=Point3(base.getAspectRatio(),0,1),
                                    other=None,
                                    blendType='easeInOut',
                                    bakeInStart=1,
                                    fluid=0,
                                    name=None)
        self.right_frame_is_active = False

        # Task that watches for the mouse going to the screen edges and slides
        # the frames onscreen when it does.
        self.prev_x = None
        self.prev_y = None
        taskMgr.add(self.task,'Mediator mouse watcher task')

        NodePathWrapper.__init__(self)
        FocusObserver.__init__(self)

    def enterNone(self):
        """Viewport focus has changed to None."""
        # Make the title of 'My Story Map' editable.
        self.myStoryMap.title['state'] = DGG.NORMAL
    def exitNone(self):
        """Undo any changes made by enterNone."""
        self.myStoryMap.title['state'] = DGG.DISABLED

    def task(self,task):
        if base.mouseWatcherNode.hasMouse():
            x=base.mouseWatcherNode.getMouseX()
            y=base.mouseWatcherNode.getMouseY()                        
            if y <= -0.87 and self.prev_y > -0.87:
                # The mouse has just moved into the bottom frame's area.
                self.activate_bottom_frame()
            elif y > -0.87 and self.prev_y <= -0.87:
                # The mouse has just moved out of the bottom frame's area.
                self.deactivate_bottom_frame()
            self.prev_y = y
            if x >= 0.8 and self.prev_x < 0.8:
                # The mouse has just moved into the right frame's area.
                self.activate_right_frame()
            elif x < 0.8 and self.prev_x >= 0.8:
                # The mouse has just moved out of the right frame's area.
                self.deactivate_right_frame()
            self.prev_x = x
        return task.cont

    def activate_bottom_frame(self):
        
        if not self.bottom_frame_is_active:
            self.bottom_interval.start()
            self.bottom_frame_is_active = True

    def deactivate_bottom_frame(self):

        if self.bottom_frame_is_active:
            self.bottom_reverse_interval.start()
            self.bottom_frame_is_active = False

    def activate_right_frame(self):        
        if not self.right_frame_is_active:
            self.right_interval.start()
            self.right_frame_is_active = True

    def deactivate_right_frame(self):
        if self.right_frame_is_active:
            self.right_reverse_interval.start()
            self.right_frame_is_active = False

    def add(self,card):
        # The Add button was pressed on one of the StoryCards in self.storyCards
        for box in self.right_vbox:
            if box.contents is None:
                box.fill(card)
                # self.activate_right_frame()
                return
        zcanvas.message('The stack is full!\nDrag another card from the stack first.')
        
    def remove(self,editableCard):
        # The Remove button was pressed on one of the StoryCards in
        # self.myStoryMap
        editableCard.getPythonTag('box').empty()
        for choosableCard in self.storyCards.items():
            if choosableCard.function == editableCard.function:
                choosableCard.enable()
                return

    # Implement the Originator interface of the memento design pattern. (For
    # saving and loading.)
    class Memento:
        """A passive class that stores the state of a Mediator object."""    
        def __init__(self, storycards, mystorymap, stack):
            # MediatorMemento just holds mementos for mediator's two StoryMap 
            # objects.
            self.storycards = storycards
            self.mystorymap = mystorymap    
            self.stack = stack
        def __str__(self):
            return self.mystorymap.__str__()
    
    def create_memento(self):
        """Return a memento object holding the current internal state of this
        object."""

        return Mediator.Memento(self.storyCards.create_memento(), 
                                self.myStoryMap.create_memento(),
                                self.right_vbox.create_memento())

    def restore_memento(self,memento):
        """Restore the internal state of this object to that held by the given
        memento."""

        self.storyCards.restore_memento(memento.storycards)
        self.myStoryMap.restore_memento(memento.mystorymap)
        self.right_vbox.restore_memento(memento.stack)

    # Implement the Caretaker interface of the memento design pattern. (For
    # saving and loading.)
    def save(self):
        """Save the current state of the application to file."""
        memento = self.create_memento()
        import datetime
        f = open(str(datetime.datetime.now()).replace(' ','_')+'.saved_story','w')
        cPickle.dump(memento,f)
        f.close()
        zcanvas.message("Saved!")

    def _load(self,args):
        self.load_list.removeNode()
        f = open(args,'r')
        memento = cPickle.load(f)
        f.close()
        self.restore_memento(memento)        
        taskMgr.doMethodLater(1, zcanvas.message, 'Welcome Message', extraArgs = ["Loaded!"])

    def load(self):
        """Restore the current state of the application from file."""
        dir = '.'
        ext = '.saved_story'
        saved_stories = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f)) and f.endswith(ext)]
        saved_stories.sort()
        
        from direct.gui.DirectGui import DirectScrolledList,DirectButton
        labels = []
        for saved_story in saved_stories:
            filename,ext = os.path.splitext(saved_story)
            l = DirectButton(text=filename, scale=0.05, command=self._load, extraArgs=[saved_story])
            labels.append(l)                
        self.load_list = DirectScrolledList(
            decButton_pos= (0.35, 0, 0.53),
            decButton_text = "/\\",
            decButton_text_scale = 0.04,
            decButton_borderWidth = (0.005, 0.005),
        
            incButton_pos= (0.35, 0, -0.02),
            incButton_text = "\\/",
            incButton_text_scale = 0.04,
            incButton_borderWidth = (0.005, 0.005),
        
            #frameSize = (0.0, 0.7, -0.05, 0.59),
            #frameColor = (1,0,0,0.5),
            pos = self.load_button.getPos(aspect2d),
            items = labels,
            numItemsVisible = 4,
            forceHeight = 0.11,
            itemFrame_frameSize = (-0.3, 0.3, -0.37, 0.11),
            itemFrame_pos = (0.35, 0, 0.4),
            )
                                
    def export(self):
        """Export the current story to a text file."""
        memento = self.create_memento()
        try:
            f = open("story.txt", "w")
            try:
                f.write(memento.__str__())
            finally:
                f.close()
        except IOError:
            print 'IOError while exporting story!'    

from direct.showbase.DirectObject import DirectObject
class WindowHandler(DirectObject):

  def __init__( self ):

    self.acceptOnce('window-event',self.windowEvent)

  def autosave(self,task):
    self.mediator.save()
    taskMgr.doMethodLater(self.auto_save_time, self.autosave, 'Auto-save task')

  def window_close(self):
    self.mediator.save()
    sys.exit(0)

  def windowEvent( self, window ):
    """
    This callback method is called when the panda window is modified.

    """
    if window is not None: # window is none if panda3d is not started
        wp = window.getProperties()
        self.mediator = Mediator()        
        self.accept('mouse1',zcanvas.zoomTo)
        #self.accept('mouse1-up',zcanvas.drop)
        self.accept('mouse3',zcanvas.zoomToParent)
        self.accept('mouse2',zcanvas.drag)
        self.accept('mouse2-up',zcanvas.drop)
        #self.accept('shift-mouse1',zcanvas.zoomTo)
        #self.accept('shift-mouse3',zcanvas.zoomToParent)
        #self.accept('shift-mouse2',zcanvas.drag)
        #self.accept('shift-mouse2-up',zcanvas.drop)
        #self.accept('z',zcanvas.zoom_in)
        #self.accept('x',zcanvas.zoom_out)
        #self.accept('z-up',zcanvas.stop_zoom_in)
        #self.accept('x-up',zcanvas.stop_zoom_out)
        
        # Auto-saving every 5 mins. and on window close.
        window.setCloseRequestEvent('close')
        self.accept(window.getCloseRequestEvent(),self.window_close)
        self.auto_save_time = 300
        taskMgr.doMethodLater(self.auto_save_time, self.autosave, 'Auto-save task')
        self.accept('escape',self.window_close)

        taskMgr.doMethodLater(1, zcanvas.message, 'Welcome Message', extraArgs = ["Welcome to the Story Maps application.\n Left-click to zoom in, middle-click to drag."])             
                        
if __name__ == '__main__':

    import direct.directbase.DirectStart 

    w = WindowHandler()
    wp = WindowProperties()
    if 'fullscreen' in sys.argv[1:]:    
        wp.setFullscreen(1)
    else:
        wp.setSize(1024,768)    
    base.win.requestProperties(wp)
    run ()