"""Unit test for box.py."""

import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import *
from znode import ZNode,Draggable

from pandac.PandaModules import *
import unittest

class TestItem(ZNode,Draggable):
    """A draggable zode with some geometry from cardmaker."""

    cm = CardMaker('cm')
    left,right,bottom,top = -.2,.2,-.2,-.2
    cm.setFrame(left,right,bottom,top)

    def __init__(self):
    
        ZNode.__init__(self,geomnode = TestItem.cm.generate())
        Draggable.__init__(self)
        self.set_draggable(True)

class BoxTest(unittest.TestCase):

    def setUp(self):
    
        pass
        
    def tearDown(self):
    
        pass

    def _testContains(self,box,item):
        """Helper method, tests that box.contents is item, item.np is attached
        to box.np, the position of item.np is the same as box.np, and item 
        has been tagged with box."""

        self.assertEqual(box.contents,item)
        self.assertEqual(box.np,item.getParent())
        self.assertEqual(box.np.getPos(render2d),item.getPos(render2d))
        self.assertEqual(item.getPythonTag("box"),box)

    def testFill(self):
        """After box.fill(item) box should contain item."""        
        b = Box()
        i = TestItem()
        b.fill(i)
        self._testContains(b,i)
   
    def testAlreadyEmptyError(self):
        """Attempting to empty an already empty box should raise 
        BoxAlreadyEmptyError."""
        
        b = Box()
        self.assertRaises(BoxAlreadyEmptyError,b.empty)

    def _testEmpty(self,box):
        """Helper method, tests that box is empty: box.contents is None."""
        self.assertEqual(box.contents,None)
        
    def _testNotPacked(self,item):
        """Helper method, tests that item is not in any box: item has no "box"
        tag, and item.np is a singleton nodepath."""        
        self.assertEqual(item.getPythonTag("box"),None)
        # FIXME. This only works for items that were previously in a box then
        # were emptied. If they were never in a boc the parent will be zcanvas.
        # Maybe just test that the parent is not any box?
        self.assertEqual(str(item.getParent()),'(empty)')

    def testEmpty(self):
        """After a box.empty() box should be empty and the item previously
        contained by box should no longer be in any box."""
        b = Box()
        i = TestItem()
        b.fill(i)
        b.empty()
        self._testEmpty(b)
        self._testNotPacked(i)

    def testReplace(self):
        """Placing a new item into an already filled box should replace the
        existing item."""

        b = Box()
        i = TestItem()
        b.fill(i)
        j = TestItem()
        b.fill(j)

        self._testContains(b,j)
        self._testNotPacked(i)

    def testChangeBoxes(self):
        """If an item currently in one box is placed into another box, the new
        box should contain the item and the old box should be empty."""
        
        b = Box()
        c = Box()
        i = TestItem()
        b.fill(i)
        c.fill(i)

        self._testContains(c,i)
        self._testEmpty(b)

    def testChangeBoxesReplace(self):
        """If an item currently in one box is placed into a new box that already
        contains an item, the new box should contain the first item, the old box
        should be empty, and the old item should have no box."""
        
        b = Box()
        c = Box()
        i = TestItem()
        j = TestItem()
        b.fill(i)
        c.fill(j)
        c.fill(i)

        self._testContains(c,i)
        self._testEmpty(b)
        self._testNotPacked(j)

    def test_do_drag_highlight(self):
        # TODO. Currently no unit test for do_drag_highlight. It should show the
        # highlight geometry and hide the unhighlight geometry. ZNode defines
        # the unhighlight geometry (what it calls just the geometry),
        # Higlightable should define the highlight geometry and the interface
        # that says when each should be shown and hidden.
        pass
        
    def test_do_drag_unhighlight(self):
        # TODO. Currently no unit test for do_drag_unhighlight. It should show
        # the unhighlight geometry and hide the highlight geometry.
        pass

    def test_dropped_onto(self):
        """After drop is called on a given box with a given draggable in
        the DroppedEvent object, the box should contain the draggable."""
        
        from znode import DroppedEvent
        from messager import messager
        b = Box()
        i = TestItem()
        dropped_event = DroppedEvent(draggable = i, startPos = (0,0,0),
                                     endPos = (0,0,0), droppable = b)
        b.drop(dropped_event)
        self._testContains(b,i)

    def test_dropped_onto_from(self):
        """After an Item is dragged from one Box and dropped onto another Box,
        the first Box should be empty and the second Box should contain the 
        Item."""
        
        from znode import DroppedEvent
        from messager import messager
        b1 = Box()
        b2 = Box()
        i = TestItem()
        b1.fill(i)
        dropped_event = DroppedEvent(draggable = i, startPos = (0,0,0),
                                     endPos = (0,0,0), droppable = b2)
        b2.drop(dropped_event)
        self._testContains(b2,i)
        self._testEmpty(b1)

    def test_droppable(self):
        """A box should be droppable when empty but not when full."""
        
        # TODO. Currently no good way to test for this.
        return

    def test_dropped_when_full(self):
        """After a 'drop done' message is sent with a given box and draggable in
        the DroppedEvent object, if the box is already full nothing should 
        change."""

        from znode import DroppedEvent
        from messager import messager
        b = Box()
        i = TestItem()
        j = TestItem()
        b.fill(i)
        # Drag an item onto an already filled box.
        dropped_event = DroppedEvent(draggable = j, startPos = (0,0,0),
                                     endPos = (0,0,0), droppable = b)
        messager.send('drop done',dropped_event)
        self._testContains(b,i)
        # Drag an item from a box and drop it onto the same box again.
        dropped_event = DroppedEvent(draggable = i, startPos = (0,0,0),
                                     endPos = (0,0,0), droppable = b)
        messager.send('drop done',dropped_event)
        self._testContains(b,i)

if __name__ == '__main__':
    unittest.main()