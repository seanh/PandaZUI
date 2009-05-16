"This module contains ZCanvas, the class that represents the zoomable canvas, and instantiates zcanvas, the singleton instance of zcanvas."

import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
from direct.gui.DirectGui import DirectLabel

from messager import messager

import sys

# Should the singleton zcanvas, as the root canvas of the scene, also represent
# an infinite surface for dropping objects onto? (i.e. implement the Droppable
# interface, and call itself whenever there is no droppable.) What would the drop 
# method do? Nothing? But then people could subclass zcanvas, and override the
# drop method to make the dropped object stay at the position it was dropped at.
# Or else the drop method could send an event and others could pick up the event
# and do something.

# Remove the infinite bounding volume on aspect2d that turns off culling on 
# aspect2d.
# This undoes an optimisation introduced by the Panda team on the assumption 
# that nobody would want to perform collision tests on node on aspect2d. Since 
# we do want to do that, we don't want this optimisation.
aspect2d.node().setFinal(False)
aspect2d.node().clearBounds()

# FIXME: make this an internal class and put it next to where it's used.
class MessageStarted:
    def __init__(self,text,duration):
        self.text = text
        self.duration = duration

# FIXME: ZCanvas is quite a big and complicated class. Can it be broken up into
# smaller classes?
class ZCanvas(object):
    """The singleton zcanvas represents the infinite and infinitely scalable
    zoomplane and manages the viewport through which the user sees the zoomplane
    (including zooming and panning the viewport). If you want to place an object 
    on the zoom plane, you must attach it to the viewport node held by zcanvas.
    
    Messages sent by zcanvas (see messager.py to subscribe to these):
    
    'new focus'     --  viewport's focused znode has changed.
                  
                        arg: the newly focused znode.
    
    'message started'   --  a new text message is being displayed on the
                            overlay.
                  
                            arg: a MessageStarted event object.
                            
    'message ended' --  a text message has finished being displayed on the
                        overlay.
                        
                        arg: None.
                            
    'zooming to znode'  --  the viewport has begun zooming to a znode.
                            
                            arg: the znode being zoomed to.
                            
    'zooming to zparent'    -- the viewport has begun zooming back to a
                               parent node of the previously focused node.
                               
                               arg: the znode being zoomed to, or None if the
                                    viewport is zooming back to its home
                                    position.
                                        
    'zoom done' --  the viewport has finished zooming to a znode.

                    arg: None.
    
    'do drag'   --  a drag signal has been received (zcanvas.drag was called).
                    
                    arg: the znode to be dragged.
                               
    'do drop'   --  a drop signal has been received (zcanvas.drop was called).
                    
                    arg: the znode currently being dragged.
    
    """

    def __init__(self):
        """Initialise the singleton zcanvas instance: setup the viewport node,
        the collision rays for mouse picking, and start the task method used
        for mouse picking, and other initialisation details.

        """
        # This is the node that is transformed to implement viewport panning and
        # zooming.
        self.viewport = aspect2d.attachNewNode('zcanvas')

        # This is the node that user classes attach nodepaths to if they want
        # them to be on the zoom plane.
        self.home = self.viewport.attachNewNode('home')
        #self.home.showTightBounds()
                
        # This interval is used when the viewport is automatically transformed
        # to focus on a given nodepath, and also when the viewport is zoomed in
        # or out manually.
        self._zoomInterval = None

        # The time (in seconds) that it takes to move the viewport from the 
        # minimum to the maximum position on the Y axis when manually zooming.
        # (Controls the speed when manually zooming the viewport.)
        self.zoom_time = 2
        
        # Minimum and maximum positions for the viewport when manually moving on
        # the Y axis. FIXME: remove these arbitrary limits?
        self.max_zoom = 4.0
        self.min_zoom = .1
        
        # Interval used to manually pan the viewport left and right, and its
        # speed and minimum and maximum positions.
        self.pan_x_interval = None
        self.pan_x_time = 2
        self.max_pan_x = 1.33
        self.min_pan_x = -1.33

        # Interval used to manually pan the viewport up and down, and its
        # speed and minimum and maximum positions.
        self.pan_z_interval = None
        self.pan_z_time = 2
        self.max_pan_z = 1.0
        self.min_pan_z = -1.0 

        # The zcanvas' collision ray, collision mask, etc. used for mouse
        # picking.
        cn = CollisionNode('zoom collision ray')
        cn.addSolid(CollisionRay(0,-100,0, 0,1,0))
        from pandac.PandaModules import BitMask32
        self.mask = BitMask32.bit(0)
        cn.setFromCollideMask(self.mask)
        cn.setIntoCollideMask(BitMask32.allOff())
        self._cnp = aspect2d.attachNewNode(cn)
        self._ctrav=CollisionTraverser()
        self._queue = CollisionHandlerQueue()
        self._ctrav.addCollider(self._cnp, self._queue)
        # For debugging only.
        # self._ctrav.showCollisions(self.viewport)

        # Attributes that record which zoomable, draggable and highlightable
        # (if any) the mouse pointer is currently over.
        self._zoomMouseOver = None
        self._dragMouseOver = None
        self._highlightMouseOver = None

        # The draggable (if any) that is currently being dragged.
        self._draggee = None

        # Task method that does the mouse picking.
        taskMgr.add(self._mouseOverTask,'_mouseOverTask')

        # The currently focused node. A managed property.
        self.__focus = None

        # Catch the 'zoom done' message from panda's messenger system and echo
        # it to my custom messager system. (Because we use
        # interval.setDoneEvent to send the 'zoom done' message it must
        # initially be sent through panda's messenger).
        base.accept('zoom done',messager.send,['zoom done'])
                
    def getfocus(self): return self.__focus

    def setfocus(self,obj):
        self.__focus = obj
        messager.send('new focus',self.focus)

    # focus is a property whose set method ensures that observer's are notified 
    # whenever it changes.
    focus = property(fget=getfocus, fset=setfocus,
                      doc ="The viewport's currently focused object.")
                    
    def message(self,text,duration=5):
        """Display a text message to the user for a given duration in seconds.
        
        """
        # If we're already displaying a message, finish it early.
        if hasattr(self,'help'):
            self.help.detachNode()
            self.sequence.finish()

        # The new message.        
        self.help = DirectLabel(text = text, text_scale=.1,
                                text_fg=(.8,.8,.8,1), frameColor=(.2,.2,.2,0), 
                                frameVisibleScale=(1.2,1.2))
        self.help.setPos(0,0,-.7)
        self.help.setAlphaScale(0) # At first the message is fully transparent.

        # This function is used to fade the message in and out.
        def fade(t):
            """Set the alpha of the message to t (multiplied by a constant 
            factor)."""
            self.help.setAlphaScale(t*.9)
            self.help.setColor(.2,.2,.2,t*.7)
            
        # Create a sequence of intervals to fade in the message, wait for
        # `duration`, then fade it out.
        fade_in = LerpFunc(fade, fromData = 0, toData = 1, duration = .5,
                           blendType = 'noBlend', extraArgs = [], name = None)
        fade_out = LerpFunc(fade, fromData = 1, toData = 0, duration = .5,
                            blendType = 'noBlend', extraArgs = [], name = None)
        self.sequence = Sequence(fade_in,Wait(duration),fade_out)
        self.sequence.setDoneEvent('message ended')
        self.sequence.start()
        messager.send('message started',MessageStarted(text,duration))

    def _mouseOverTask(self,t):
        """Move the CollisionRay to the position of the mouse pointer, check
        for collisions, and update various attributes related to what nodes the
        mouse is over.

        """
        if not base.mouseWatcherNode.hasMouse():
            # The mouse is outside of the window, do nothing.
            return Task.cont

        # Do the collision test.
        np = self._findCollision()

        # The zoomable, draggable, droppable and highlightable classes set
        # `self` as a python tag on the nodepaths that they wrap. We use these 
        # tags to find out if np is below the nodepath of a zoomable, draggable,
        # droppable or highlightable in the scene graph.

        prevHighlightMouseOver = self._highlightMouseOver

        if self._draggee is not None:
            # Something is being dragged, so search for a droppable.
            if np is not None:
                # Find the nearest droppable that is an ancestor to np, if any.
                self._highlightMouseOver = np.getNetPythonTag('droppable')
            else:
                self._highlightMouseOver = None
        else:
            # Nothing is being dragged, so search for a zoomable, a draggable
            # and a highlightable.
            # FIXME: zoomable and draggable only really need to be searched for
            # when the zoom and drag buttons are clicked.
            if np is not None:
                   
                # Find the nearest zoomable that is an ancestor of np, if any.
                self._zoomMouseOver = np.getNetPythonTag('zoomable')

                # Find the nearest draggable that is an ancestor to np, if any.
                self._dragMouseOver = np.getNetPythonTag('draggable')
            
                # Find the nearest highlightable that is an ancestor to np, if any.
                self._highlightMouseOver = np.getNetPythonTag('highlightable')
            else:
                self._zoomMouseOver = None
                self._dragMouseOver = None
                self._highlightMouseOver = None

        # Highlight and unhighlight nodes as necessary.
        if prevHighlightMouseOver != self._highlightMouseOver:
            if prevHighlightMouseOver is not None:
                prevHighlightMouseOver.unhighlight()
            if self._highlightMouseOver is not None:
                self._highlightMouseOver.highlight()

        return Task.cont

    def _findCollision(self):        
        """Helper method for _mouseOverTask. Move the CollisionRay ray to be
        over the mouse pointer, run a collision test, and return the first
        nodepath that the ray collides with, or None if nothing is hit. Also
        return None if the mouse is over a DirectGUI object.

        returns -- NodePath or None.
        """
        # If the mouse is over a DirectGUI object then zcanvas doesn't test
        # for collisions. (Leave it to DirectGUI to handle mouse-overs of 
        # DirectGUI objects.)
        if base.mouseWatcherNode.isOverRegion():
            return None

        # Move the CollisionRay's NodePath to where the mouse pointer is.
        mpos = base.mouseWatcherNode.getMouse()
        self._cnp.setPos(render2d,mpos[0],0,mpos[1])

        # Run the collision  test.
        self._ctrav.traverse(aspect2d)
        
        if self._queue.getNumEntries() == 0:
            # The ray didn't collide with anything.
            return None

        # FIXME: what we need to return here is the nodepath, of those in the
        # queue, that would be rendered last and appear on top of the others,
        # i.e. the one that is rightmost and lowest in the scene graph. If the
        # collision system walks the scene graph top-to-bottom and left-to-right
        # then that should be the last nodepath in the queue. For now, we guess
        # that that is correct.
        #
        # If this breaks down, we can try setting non-zero Y-values on the 
        # nodepaths corresponding to their conceptual Y-order, and see if that
        # allows us to use queue.sort(), or if that doesn't work, introduce my
        # own Y-order attribute to my classes.
        np = self._queue.getEntry(self._queue.getNumEntries()-1).getIntoNodePath()
        return np

    def zoomTo(self):
        """
        If the mouse pointer is over a zoomable and we are not already zooming,
        focus the viewport on the zoomable that the mouse pointer is over.

        """
        if self.isZooming():
            # If we are already in the process of zooming we don't want to
            # initiate another zoom.
            return
        elif self._zoomMouseOver is None:
            # The mouse pointer is not over any zoomable.
            return
        else:
            self._zoomToNodePath(self._zoomMouseOver.np)
            self.focus = self._zoomMouseOver
            messager.send('zooming to znode',self._zoomMouseOver)

    # Rename this to auto_zoom_out?
    def zoomToParent(self):
        """
        If self.focus is not None and we are not already zooming, focus the
        viewport on the next zoomable above self.focus in the scene graph, or
        if there is no such zoomable, move the viewport to it's home position.

        """
        if self.focus is not None and not self.isZooming():
            p = self.focus.getParent().getNetPythonTag('zoomable')
            if p is None:
                self._zoomToNodePath(self.home)
                self.focus = None
            else:
                self._zoomToNodePath(p.np)
                self.focus = p
            messager.send('zooming to zparent',self.focus)

    def drag(self):
        """Begin dragging the draggable that is currently under the mouse 
        pointer, if any."""

        if self._dragMouseOver is not None:
            self._draggee = self._dragMouseOver
            self._dragMouseOver = None
            self._zoomMouseOver = None
            messager.send('do drag',self._draggee)
            self._draggee.drag()

    def drop(self):
        """Drop the node currently being dragged, if any."""

        if self._draggee is not None:
            messager.send('do drop',self._draggee)
            self._draggee.drop()
            self._draggee = None

    # FIXME: this should be a module-level utility function somewhere, not an
    # instance method.
    def find_center(self,bottom_left,top_right):
        """Given two points bottom_left and top_right representing opposite
        corners of a rectangular region (e.g. a bounding box returned by
        NodePath.getTightBounds()), return a point representing the center of
        the rectangular region.
        
        returns : Point3
        
        """
        l = bottom_left.getX()
        b = bottom_left.getZ()
        r = top_right.getX()
        t = top_right.getZ()
        center_x = l + ((r-l)/2.0)
        center_z = b + ((t-b)/2.0)
        center = Point3(center_x,0,center_z)
        return center

    def _zoomToNodePath(self,np):
        """Create and start an interval that will move the viewport to
        focus on the nodepath np.

        """
        # ynjh_jo's zoom code.
        posZoom=self.viewport.getRelativePoint(np.getParent(),self.find_center(*np.getTightBounds()))
        bounds3 = np.getTightBounds()
        oldScale = self.viewport.getScale()
        self.viewport.setScale(1,1,1)
        bounds = render2d.getRelativeVector(np.getParent(),bounds3[1]-bounds3[0])
        self.viewport.setScale(oldScale)
        selfRatio = base.getAspectRatio()*bounds[0]/bounds[2]
        maxScale = 2./bounds[2*( selfRatio<base.getAspectRatio() )]
        zoomable = np.getPythonTag('zoomable')
        if zoomable is not None:        
            maxScale *= zoomable.magnification
        else:
            maxScale *= 0.8 # Hard-coded magnification factor for home node.
        self.zoomInterval = self.viewport.posHprScaleInterval(.5,
            -posZoom*maxScale,
            self.viewport.getHpr(),
            Vec3(maxScale,1,maxScale)
            )
        self.zoomInterval.setDoneEvent('zoom done')            
        self.zoomInterval.start()

    def _zoomToHome(self):
        """Create and start an interval that will move the viewport back
        to its home position.

        """
        # ynjh_jo's code again.
        self._zoomInterval = self.viewport.posHprScaleInterval(
            duration = .5,
            pos = Point3(0,0,0),
            hpr = self.viewport.getHpr(),
            scale = Vec3(1,1,1)
            )
        self.zoomInterval.setDoneEvent('zoom done')    
        self._zoomInterval.start()

    def isZooming(self):
        """Return True if the viewport is currently zooming in or out, False if
        it is not.
        
        """
        if self._zoomInterval is None:
            return False
        elif self._zoomInterval.isPlaying():
            return True
        else:
            return False

    # Methods for manual panning and zooming.
    # FIXME. This don't interact nicely with the automatic zooming above, and
    # they don't generate any events. 
    def zoom_in(self):

        if self._zoomInterval is not None:
            if self._zoomInterval.isPlaying():
                self._zoomInterval.pause()

        current_zoom = self.viewport.getScale().getY()
        duration = ((self.max_zoom-current_zoom)/self.max_zoom)*self.zoom_time

        self._zoomInterval = self.viewport.scaleInterval(
            duration=duration,
            scale=4,
            name = "zoom_in")
        self._zoomInterval.start()

    def zoom_out(self):

        if self._zoomInterval is not None:
            if self._zoomInterval.isPlaying():
                self._zoomInterval.pause()
   
        current_zoom = self.viewport.getScale().getY()
        duration = ((current_zoom-self.min_zoom)/self.max_zoom)*self.zoom_time
       
        self._zoomInterval = self.viewport.scaleInterval(
            duration=.5,
            scale=.1,
            name = "zoom_out")
        self._zoomInterval.start()

    def stop_zoom_in(self):
   
        if self._zoomInterval is not None:
            if self._zoomInterval.isPlaying() and self._zoomInterval.getName() == "zoom_in":
                self._zoomInterval.pause()

    def stop_zoom_out(self):
   
        if self._zoomInterval is not None:
            if self._zoomInterval.isPlaying() and self._zoomInterval.getName() == "zoom_out":
                self._zoomInterval.pause()

    def pan_left(self):

        if self.pan_x_interval is not None:
            if self.pan_x_interval.isPlaying():
                self.pan_x_interval.pause()

        current_pan = self.viewport.getPos().getX()
        duration = ((self.max_pan_x-current_pan)/self.max_pan_x)*self.pan_x_time

        self.pan_x_interval = self.viewport.posInterval(
            duration=duration,
            pos = Vec3(self.max_pan_x,self.viewport.getPos().getY(),self.viewport.getPos().getZ()),
            name = "pan_left")
        self.pan_x_interval.start()

    def pan_right(self):

        if self.pan_x_interval is not None:
            if self.pan_x_interval.isPlaying():
                self.pan_x_interval.pause()

        current_pan = self.viewport.getPos().getX()
        duration = ((current_pan-self.min_pan_x)/self.max_pan_x)*self.pan_x_time

        self.pan_x_interval = self.viewport.posInterval(
            duration=duration,
            pos = Vec3(self.min_pan_x,self.viewport.getPos().getY(),self.viewport.getPos().getZ()),
            name = "pan_right")
        self.pan_x_interval.start()

    def stop_pan_left(self):
   
        if self.pan_x_interval is not None:
            if self.pan_x_interval.isPlaying() and self.pan_x_interval.getName() == "pan_left":
                self.pan_x_interval.pause()

    def stop_pan_right(self):
   
        if self.pan_x_interval is not None:
            if self.pan_x_interval.isPlaying() and self.pan_x_interval.getName() == "pan_right":
                self.pan_x_interval.pause()

    def pan_down(self):

        if self.pan_z_interval is not None:
            if self.pan_z_interval.isPlaying():
                self.pan_z_interval.pause()

        current_pan = self.viewport.getPos().getZ()
        duration = ((self.max_pan_z-current_pan)/self.max_pan_z)*self.pan_z_time

        self.pan_z_interval = self.viewport.posInterval(
            duration=duration,
            pos = Vec3(self.viewport.getPos().getX(),self.viewport.getPos().getY(),self.max_pan_z),
            name = "pan_down")
        self.pan_z_interval.start()

    def pan_up(self):

        if self.pan_z_interval is not None:
            if self.pan_z_interval.isPlaying():
                self.pan_z_interval.pause()

        current_pan = self.viewport.getPos().getZ()
        duration = ((current_pan-self.min_pan_z)/self.max_pan_z)*self.pan_z_time

        self.pan_z_interval = self.viewport.posInterval(
            duration=duration,
            pos = Vec3(self.viewport.getPos().getX(),self.viewport.getPos().getY(),self.min_pan_z),
            name = "pan_up")
        self.pan_z_interval.start()

    def stop_pan_up(self):
   
        if self.pan_z_interval is not None:
            if self.pan_z_interval.isPlaying() and self.pan_z_interval.getName() == "pan_up":
                self.pan_z_interval.pause()

    def stop_pan_down(self):
   
        if self.pan_z_interval is not None:
            if self.pan_z_interval.isPlaying() and self.pan_z_interval.getName() == "pan_down":
                self.pan_z_interval.pause() 

zcanvas = ZCanvas()
