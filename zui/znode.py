"""
This module contains NodePathWrapper, a class that simply wraps a NodePath object, and ZNode, a subclass of NodePathWrapper that adds a GeomNode to the NodePath and implements the zoom protocol to allow the viewport to automatically zoom and pan to come to focus on the NodePath. (ZNode is sometimes referred to as 'zoomable'.) The rest of the classes, FocusObserver, Highlightable, Draggable and Droppable are mixin classes that are designed to be multiply inherited alongside NodePathWrapper or ZNode and provide additionally functionality.

Note that although the mixin classes do not themselves inherit NodePathWrapper, they assume the presence of NodePathWrapper in their inheritance tree, so the mixin classes can only be used by multiply inheriting them alongside either NodePathWrapper or ZNode.

"""
from zcanvas import zcanvas
from messager import messager,Receiver

from pandac.PandaModules import *
from direct.task import Task
from direct.fsm.FSM import FSM

class NodePathWrapper(Receiver):
    """A class that wraps a NodePath and forwards some useful NodePath methods.
    This is the base class for the rest of the classes in this module.

    """
    def __init__(self,np=None):
        """Initialise a NodePathWrapper object that wraps the NodePath np, or if
        no np is given, create a new NodePath and wrap  that.
        
        Optional arguments:
        
        np  -- the NodePath to wrap.
        
        """
        if np is None:
            self.np = NodePath('')
        else:
            self.np = np

    # For convenience, expose some NodePath methods directly.
    # FIXME: Should probably just use the __getattr__ trick to forward all
    # nodepath methods.
     
    # Getters.
    def getPos(self,*args):
        return self.np.getPos(*args)    
    def getX(self,*args):
        return self.np.getX(*args)    
    def getY(self,*args):
        return self.np.getY(*args)    
    def getZ(self,*args):
        return self.np.getZ(*args)
    def getScale(self,*args):
        return self.np.getScale(*args)
    def getTightBounds(self,*args):
        return self.np.getTightBounds(*args)
    def getColor(self,*args):
        return self.np.getColor(*args)
    def getParent(self,*args):
        return self.np.getParent(*args)
    
    # Setters.
    def setPos(self,*args):
        return self.np.setPos(*args)    
    def setX(self,*args):
        return self.np.setX(*args)
    def setY(self,*args):
        return self.np.setY(*args)
    def setZ(self,*args):
        return self.np.setZ(*args)
    def setScale(self,*args):
        return self.np.setScale(*args)
    def setColor(self,*args):
        return self.np.setColor(*args)
    def setTexture(self,*args):
        return self.np.setTexture(*args)
    def setTransparency(self,*args):
        return self.np.setTransparency(*args)

    # Tagging.
    def setPythonTag(self,*args):
        return self.np.setPythonTag(*args)
    def hasPythonTag(self,*args):
        return self.np.hasPythonTag(*args)
    def getPythonTag(self,*args):
        return self.np.getPythonTag(*args)
    def clearPythonTag(self,*args):
        return self.np.clearPythonTag(*args)
    def hasNetPythonTag(self,*args):
        return self.np.hasPythonTag(*args)
    def findNetPythonTag(self,*args):
        return self.np.findNetPythonTag(*args)
    def getNetPythonTag(self,*args):
        return self.np.getNetPythonTag(*args)

    # Misc.
    def reparentTo(self,*args):
        return self.np.reparentTo(*args)    
    def hide(self,*args):
        return self.np.hide(*args)
    def show(self,*args):
        return self.np.show(*args)
    def attachNewNode(self,*args):
        return self.np.attachNewNode(*args)
    def detachNode(self,*args):
        return self.np.detachNode(*args)
    def instanceUnderNode(self,*args):
        return self.np.instanceUnderNode(*args)
    def setColorOff(self,*args):
        return self.np.setColorOff(*args)
    def setBin(self,*args):
        return self.np.setBin(*args)
    def clearBin(self,*args):
        return self.np.clearBin(*args)

    # Some additional convenience methods on top of NodePath.
    def bottom_left(self):
        # getTightBounds will return a bounding box that covers the nodepath and
        # all of its children.
        return self.getTightBounds()[0]        
    def top_right(self):
        return self.getTightBounds()[1]
    def left(self):
        return self.bottom_left().getX()    
    def right(self):
        return self.top_right().getX()    
    def bottom(self):
        return self.bottom_left().getZ()    
    def top(self):
        return self.top_right().getZ()    
    def top_left(self):
        return Point3(self.left(),0,self.top())
    def bottom_right(self):
        return Point3(self.right(),0,self.bottom())

class FocusObserver:
    """A mixin class that subscribes to the messages sent by zcanvas when the
    viewport's focused node changes."""

    def __init__(self):
        """Subscribe to the 'new focus' message from zcanvas and initialise the
        finite state machine used to respond to focus changes."""
        
        self.accept('new focus',self.notify)
        # FIXME: FocusObserver never unsubscribes from the message. When should
        # it detach unsubscribe?

        class FocusFSM(FSM):
            """A finite state machine that changes state according to the
            viewport's focused object. As a side effect of changing state,
            methods of the outer class are called.

            """
            def __init__(self,outer):
                self.enterSelf = outer.enterSelf
                self.exitSelf = outer.exitSelf
                self.enterParent = outer.enterParent
                self.exitParent = outer.exitParent
                self.enterSibling = outer.enterSibling
                self.exitSibling = outer.exitSibling
                self.enterNone = outer.enterNone
                self.exitNone = outer.exitNone
                self.enterOther = outer.enterOther
                self.exitOther = outer.exitOther
                FSM.__init__(self,'FocusFSM')

        self.focus_fsm = FocusFSM(self)
        self.focus_fsm.request('None')

    # Subclasses should override these state change methods to respond to
    # viewport focus changes.
    def enterNone(self):
        """Viewport focus has changed to None."""
        pass
    def exitNone(self):
        """Undo any changes made by enterNone."""
        pass

    def enterSelf(self):
        """Viewport focus has changed to this znode."""
        pass
    def exitSelf(self):
        """Undo any changes made by enterSelf."""
        pass

    def enterParent(self):
        """Viewport focus has changed to the lowest zoomable ancestor node of
        this znode."""
        pass
    def exitParent(self):
        """Undo any changes made by enterParent."""
        pass
        
    def enterSibling(self):
        """Viewport focus has changed to a sibling znode of this znode."""
        pass
    def exitSibling(self):
        """Undo any changes made by enterSibling."""
        pass

    def enterOther(self):
        """Viewport focus has changed to some other znode."""
        pass
    def exitOther(self):
        """Undo any changes made by enterOther."""
        pass
    
    def notify(self,focus):
        """The viewport's focused object is now f, change state accordingly."""

        zparent = self.getParent().getNetPythonTag('zoomable')
        if focus is not None:
            focus_zparent = focus.getParent().getNetPythonTag('zoomable')
        else:
            focus_zparent = None

        if focus is None:
            # The viewport is not focused on any znode.
            self.focus_fsm.request('None')
        elif focus == self:
            # The viewport is focused on this znode.
            self.focus_fsm.request('Self')
        elif focus == zparent and zparent is not None:
            # The viewport is focused on the lowest zoomable ancestor node of
            # this node.
            self.focus_fsm.request('Parent')
        elif focus_zparent == zparent:
            # The viewport is focused on a sibling znode of this znode.
            self.focus_fsm.request('Sibling')
        else:
            # The viewport is focused on some other znode.
            self.focus_fsm.request('Other')

class Highlightable:   
    """A mixin class that receives notifications from zcanvas when the mouse
    pointer enters or leaves its nodepath. These events can be used to highlight
    a nodepath as the mouse cursor moves over it. The default implementation
    scales the nodepath to 120% of its original size over a 0.2 second interval
    when the mouse enters the nodepath, and scales it back over the same amount
    of time when the mouse leaves."""

    def __init__(self):
            
        pass

    def highlight(self):
        """The mouse pointer has entered the bounds of this nodepath. Subclasses
        should override this method to implement custom mouse-over behaviour.
        
        """        
        # If we are already scaling up, do nothing.
        if  hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            return

        # If we are in the process of scaling down, finish it off immediately.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            self.scaleDownInterval.finish()
        
        from direct.interval.IntervalGlobal import LerpScaleInterval        
        self.prevScale = self.getScale()
        self.scaleUpInterval = LerpScaleInterval(self.np, duration=0.2, scale=self.getScale()*1.2, startScale=self.getScale())
        self.scaleUpInterval.start()

    def unhighlight(self):
        """The mouse pointer has left the bounds of this nodepath. Subclasses 
        should override this method to implement custom mouse-over behaviour.
        
        """
        # If we are already scaling down, do nothing.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            return

        # If we are in the process of scaling up, stop.
        if  hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            self.scaleUpInterval.pause()
        
        from direct.interval.IntervalGlobal import LerpScaleInterval
        self.scaleDownInterval = LerpScaleInterval(self.np, duration=0.2, scale=self.prevScale, startScale=self.getScale())
        self.scaleDownInterval.start()

    def set_highlightable(self,boolean):
        """Enable or disable mouse-over highlighting of this nodepath. (When
        disabled, the highlight and unhighlight methods will not be
        called.)
        
        """    
        # Finish any intervals that are playing.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            self.scaleDownInterval.finish()
        elif hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            self.scaleUpInterval.finish()
    
        # Reset the scale.
        if hasattr(self,'prevScale'):
            self.setScale(self.prevScale)

        if boolean:
            self.np.setPythonTag("highlightable",self)
        else:    
            self.np.clearPythonTag("highlightable")

class DroppedEvent:
    """A simple class to record the event when a draggable object is dropped."""
    
    def __init__(self,draggable,startPos,endPos,droppable=None):
        self.draggable = draggable
        self.startPos = startPos
        self.endPos = endPos
        self.droppable = droppable
        
    def __str__(self):
        return str(self.draggable) + str(self.startPos) + str(self.endPos) + str(self.droppable)

# FIXME: Droppable should inherit Highlightable to get the scaling up and down 
# behaviour.
class Droppable:
    """An object that can be dropped onto. (Part of the Drag & Drop protocol.)

    Initially droppable is disabled, users must call set_droppable(True) to
    enable it.

    """
    def __init__(self):

        pass        

    def drop(self,event):
        """A draggable has been dropped onto this droppable.
        Subclasses should extend this if they want to do something."""
        
        # Finish any intervals that are playing.
        # FIXME: this tightly couples Droppable to Highlightable. Move this code
        # into highlightable.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            self.scaleDownInterval.finish()
        elif hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            self.scaleUpInterval.finish()
        # Reset the scale.
        if hasattr(self,'prevScale'):
            self.setScale(self.prevScale)                
        
    def set_droppable(self,b):
        """Enable or disable dropping onto the NodePath."""

        # FIXME: move this into Highlightable.
        # Finish any intervals that are playing.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            self.scaleDownInterval.finish()
        elif hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            self.scaleUpInterval.finish()
        # Reset the scale.
        if hasattr(self,'prevScale'):
            self.setScale(self.prevScale)
        
        if b is True:
            self.np.setPythonTag('droppable',self)
        else:
            self.np.clearPythonTag('droppable')

    def highlight(self):
        """Subclasses should override this method to implement custom drag-over
        behaviour."""
        
        # If we are already scaling up, do nothing.
        if  hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            return
        # If we are in the process of scaling down, finish it off immediately.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            self.scaleDownInterval.finish()
  
        from direct.interval.IntervalGlobal import LerpScaleInterval        
        self.prevScale = self.getScale()
        self.scaleUpInterval = LerpScaleInterval(self.np, duration=0.2, scale=self.getScale()*1.2, startScale=self.getScale())
        self.scaleUpInterval.start()
    
    def unhighlight(self):
        """Subclasses should override this method to implement custom drag-over
        behaviour."""
        
        # If we are already scaling down, do nothing.
        if  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            return
        # If we are in the process of scaling up, stop.
        if  hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            self.scaleUpInterval.pause()        
        from direct.interval.IntervalGlobal import LerpScaleInterval
        self.scaleDownInterval = LerpScaleInterval(self.np, duration=0.2, scale=self.prevScale, startScale=self.getScale())
        self.scaleDownInterval.start()

class DragOverEnter:
    """This class represents a drag-over-enter event, draggee has been dragged
    into the bounds of droppee."""
    def __init__(self,draggee,droppee):
        self.draggee = draggee
        self.droppee = droppee

class DragOverLeave:
    """This class represents a drag-over-leave event, draggee has been dragged
    out of the bounds of droppee."""
    def __init__(self,draggee,droppee):
        self.draggee = draggee
        self.droppee = droppee

class Draggable:
    """Enables dragging and dropping of the NodePath.
    
    Initially drag is disabled, users must call set_draggable(True) to enable
    it.
    
    Events raised by DraggableMixin:
    
    'drop done' --  after DraggableMixin has responded to a drop event.
    
                    arg: a DroppedEvent object.

    'drag over enter'   --  the mouse cursor has entered the bounds of some 
                            droppable znode while dragging this znode.
                            
                            arg: a DragOverEnter event object.

    'drag over leave'   --  the mouse cursor has left the bounds of some 
                            droppable znode while dragging this znode.
                            
                            arg: a DragOverLeave event object.

    """
    def __init__(self):
                    
        # Initialise the CollisionRay that this object uses when it is being
        # dragged to detect if the mouse pointer is over any droppable object.
        cn = CollisionNode('drag collision ray')
        cn.addSolid(CollisionRay(0,-100,0, 0,1,0))
        cn.setFromCollideMask(zcanvas.mask)
        cn.setIntoCollideMask(BitMask32.allOff())
        self._cnp = self.np.attachNewNode(cn)
        self._ctrav=CollisionTraverser()
        self._queue = CollisionHandlerQueue()
        self._ctrav.addCollider(self._cnp, self._queue)
        # self._ctrav.showCollisions(zcanvas.home)
        
        # When this object is being dragged this attribute records the 
        # droppable object that the mouse pointer is currently over, if any. 
        self._mouseOver = None

    def set_draggable(self,b):
        """Enable or disable dragging of this nodepath. (When disabled, drag
        and drop will not be called.)"""
        
        if b is True:
            self.np.setPythonTag('draggable',self)
        else:
            self.np.clearPythonTag('draggable')

    def drag(self):
        """Signal from zcanvas that the user has started to drag this
        nodepath.
        
        """
        self.prevCollideMask = self.np.getCollideMask()
        self.np.setCollideMask(BitMask32.allOff())
        self._dragTask = taskMgr.add(self._drag,'_dragTask')
        self._draggedFrom = self.getPos()
        self.setBin('gui-popup',0)         
        
    def drop(self):
        """Signal from zcanvas that the user has dropped this nodepath. By
        default a Draggable resets itself to its state before it was dragged,
        then sends an event containing a DroppedEvent object. For the benefit of
        subclasses that want to extend this method, it returns the DroppedEvent
        as well."""
        
        # This is a hack to make drag-n-drop into boxlists not be effected by
        # the scaling up and down done by Highlightable. It tightly couples
        # Draggable to Highlightable. A better way might be to make
        # Highlightable listen for the drag and drop signals and immediately
        # reset the state when it gets them.
        if  hasattr(self,'scaleUpInterval') and self.scaleUpInterval.isPlaying():
            self.scaleUpInterval.finish()            
        elif  hasattr(self,'scaleDownInterval') and self.scaleDownInterval.isPlaying():
            self.scaleDownInterval.finish()
        if hasattr(self,'prevScale'):
            self.setScale(self.prevScale)
        
        dropped_event = DroppedEvent(draggable = self,
                                     startPos = self._draggedFrom,
                                     endPos = self.getPos(),
                                     droppable = zcanvas._highlightMouseOver)
       
        # Reset the state of this object to how it was before the drag began.
        self.clearBin()
        self.np.setCollideMask(self.prevCollideMask)
        taskMgr.remove(self._dragTask)
        self.setPos(self._draggedFrom)
                
        if self._mouseOver is not None:
            messager.send('drag over leave',DragOverLeave(self,self._mouseOver))
            self._mouseOver = None
            
        messager.send('drop done',dropped_event)                
        if zcanvas._highlightMouseOver is not None:
            zcanvas._highlightMouseOver.drop(dropped_event)
                    
    def _drag(self,task):
        """Task method used when this node is being dragged. Updates the
        position of this object to follow the mouse pointer."""

        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.np.setPos(render2d,mpos[0],0,mpos[1])
        return task.cont                              
                                      
class ZNode(NodePathWrapper):
    """A nodepath with an attached geomnode that can be automatically zoomed and
    panned to by the viewport (a 'zoomable' node.)

    """        
    def __init__(self,geomnode=None,magnification=1):
        """        
        Optional arguments:
        
        frame -- (left,right,bottom,top) size of frame to create

        """                    
        NodePathWrapper.__init__(self)
                                 
        # This attribute is read by zcanvas to determine how far to zoom in
        # when zooming to this ZNode.
        self.magnification = magnification

        # As well as being the visible representation of the ZNode, a ZNode's
        # geometry is used by zcanvas for collision detection when mouse
        # picking.
        if geomnode is None:
            cm = CardMaker('Node created by CardMaker')            
            cm.setFrame(-.3,.3,-.4,.4)
            self.geomnode = cm.generate()
        else:
            self.geomnode = geomnode            
        self.geomnodepath = self.attachNewNode(self.geomnode)        
        self.geomnode.setIntoCollideMask(self.geomnode.getIntoCollideMask() | zcanvas.mask)            
            
    def set_zoomable(self,b):
        """Enable or disable zooming to this ZNode."""
        
        if b is True:
            self.np.setPythonTag('zoomable',self)
        else:
            self.np.clearPythonTag('zoomable')
