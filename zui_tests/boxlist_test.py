"""Unit test for boxlist.py"""

import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import *
from boxlist import *
from znode import ZNode

from pandac.PandaModules import *
import unittest

class TestItem(ZNode):
    """Just a ZNode with some geometry from CardMaker. This class is pointless
    really because ZNode will create some similar geometry by default anyway."""

    cm = CardMaker('cm')
    left,right,bottom,top = -.2,.2,-.2,-.2
    cm.setFrame(left,right,bottom,top)

    def __init__(self):
    
        ZNode.__init__(self,geomnode = TestItem.cm.generate())

class TestAddingAndRemoving(unittest.TestCase):
    """Test all the different boxlist methods for adding, removing and accessing
    boxes and items."""

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def testAppendBox(self):
        """After a box has been appended to a boxlist, the box's node's parent
        in the scene graph should be the boxlist's node, the box's boxlist
        attribute should be the boxlist, and the length of the boxlist should be
        1."""
        
        l = BoxList()
        b = Box()
        l.append(b)
        self.assertEqual(b.np.getParent(),l.np)
        self.assertEqual(b.boxlist,l)
        self.assertEqual(len(l),1)
    
    def testAppendAndGet(self):
        """Should be able to append boxes to a boxlist and then retrieve them
        with []-notation."""
        
        l = BoxList()
        b1, b2, b3 = Box(), Box(), Box()
        l.append(b1)
        l.append(b2)
        l.append(b3)
        self.assertEqual(l[0],b1)    
        self.assertEqual(l[1],b2)
        self.assertEqual(l[2],b3)
        self.assertEqual(len(l),3)
        
    def testExtendAndGet(self):
        """Should be able to extend a boxlist with a sequence of boxes and then
        get the same boxes out again."""
        
        l = BoxList()
        b1, b2, b3 = Box(), Box(), Box()
        l.extend((b1,b2,b3))
        self.assertEqual(l[0],b1)
        self.assertEqual(l[1],b2)
        self.assertEqual(l[2],b3)
        self.assertEqual(len(l),3)

    def testInsert(self):
        """Should be able to insert a box into a list and get it out again using
        the same index."""

        l = BoxList()        
        a, b, c = Box(), Box(), Box()
        l.extend((a,b,c))
        d = Box()
        l.insert(1,d)
        self.assertEqual(l[1],d)
        self.assertEqual(len(l),4)

    def testContains(self):
        """Contains should return True if the box is in the boxlist, False 
        otherwise."""

        l = BoxList()        
        a, b, c = Box(), Box(), Box()
        d = Box()
        l.extend((a,b,c))
        self.assert_(b in l)
        self.assert_(d not in l)
        l.append(d)
        self.assert_(d in l)
        del l[3]
        self.assert_(d not in l)
                
    def testDel(self):
        """After a box has been deleted from a boxlist it should no longer be
        found in the boxlist, the boxlist attribute of the box should be None,
        and the box's nodepath should be a singleton nodepath."""        

        l = BoxList()        
        a, b, c = Box(), Box(), Box()
        l.extend((a,b,c))
        del l[2]
        self.assertEqual(len(l),2)
        self.assert_(c not in l)
        self.assertEqual(c.boxlist,None)
        self.assertEqual(str(c.getParent()),'(empty)')

    def testMove(self):
        """If a box is added to a new boxlist when it was already contained in
        another boxlist, it should be added to the new list and deleted from the
        old one."""
        
        l1 = BoxList()
        l2 = BoxList()
        b = Box()
        l1.append(b)
        l2.append(b)

        self.assertEqual(b.np.getParent(),l2.np)
        self.assertEqual(b.boxlist,l2)
        self.assert_(b in l2)
        self.assertEqual(l2[0],b)
        self.assertEqual(len(l2),1)

        self.assertEqual(len(l1),0)
        self.assert_(b not in l1)

    def testSet(self):
        """If a box in a boxlist is replaced by another box, the replaced box
        should no longer be found in the boxlist, its box attribute should be
        None, and its nodepath should be a singleton nodepath. The new box
        should be found in the boxlist, its box attribute should be the boxlist,
        and its nodepaths parent should be the boxlists nodepath. Replacing a
        box should not change the length of the boxlist."""

        l = BoxList()
        b1 = Box()
        l.append(b1)
        b2 = Box()
        l[0] = b2
                
        self.assertEqual(b2.np.getParent(),l.np)
        self.assertEqual(b2.boxlist,l)
        self.assertEqual(l[0],b2)

        self.assert_(b1 not in l)
        self.assertEqual(b1.boxlist,None)
        self.assertEqual(str(b1.getParent()),'(empty)')

        self.assertEqual(len(l),1)

    def testItems(self):
        """Items contained in boxes contained in a boxlist should be found in
        the list returned by boxlist.items(), and only those items should be
        found in the list, and they should be in the right order."""
        
        i1,i2,i3 = TestItem(),TestItem(),TestItem()
        b1,b2,b3 = Box(),Box(),Box()
        b1.fill(i1)
        b2.fill(i2)
        b3.fill(i3)
        l = BoxList()
        l.extend((b1,b2,b3))
        self.assertEqual(i1,l.items()[0])
        self.assertEqual(i2,l.items()[1])
        self.assertEqual(i3,l.items()[2])
        self.assertEqual(len(l.items()),3)
        b3.empty()
        self.assert_(i3 not in l.items())
        self.assertEqual(l.items()[2],None)
        self.assertEqual(len(l.items()),3)
        del l[2]        
        self.assertEqual(len(l.items()),2)
        del l[1]
        self.assertEqual(len(l.items()),1)
        self.assert_(i2 not in l.items())
        del l[0]
        self.assert_(i1 not in l.items())
        self.assertEqual(len(l.items()),0)
        	        
class LoggerBoxList(BoxList):
    """A BoxList subclass that logs all calls of the layout method."""
    
    def __init__(self):
    
        BoxList.__init__(self)
        self.log = 0
        
    def layout(self):
    
        self.log += 1

class TestCallsToLayout(unittest.TestCase):
    """Tests to ensure that the layout() method of BoxList is called at all the
    right times."""

    def setUp(self):
        self.l = LoggerBoxList()        
        self.a, self.b, self.c, self.d = Box(), Box(), Box(), Box()
        self.l.extend((self.a,self.b,self.c,self.d))
        self.l.log = 0 # Reset the log, ready for the tests to begin.
        
    def tearDown(self):
        pass    
        
    def testFill(self):
        """The layout() method should be called once when a box belonging to the
        boxlist is filled."""

        self.l[0].fill(TestItem())
        self.assertEqual(self.l.log,1)
        self.c.fill(TestItem())
        self.assertEqual(self.l.log,2)
        self.a.fill(TestItem())
        self.assertEqual(self.l.log,3)

    def testEmpty(self):
        """The layout() method should be called once when a box belonging to the 
        boxlist is emptied."""    

        i, j = TestItem(), TestItem()
        self.b.fill(i)
        self.d.fill(j)
        self.l.log = 0
        self.l[1].empty()
        self.assertEqual(self.l.log,1)
        self.l[3].empty()
        self.assertEqual(self.l.log,2)

    def testEmptyException(self):
        """The layout() method should not be called if empty() is called on an
        already empty box in the boxlist."""
        
        try:
            self.a.empty()
        except BoxAlreadyEmptyError:
            pass
        self.assertEqual(self.l.log,0)

    def testAppend(self):
        """The layout() method should be called once when a box is appended to a
        boxlist."""
        
        self.l.append(Box())
        self.assertEqual(self.l.log,1)

    def testInsert(self):
        """The layout() method should be called once when a box is inserted into
        a boxlist."""
        
        self.l.insert(1,Box())
        self.assertEqual(self.l.log,1)
         
    def testExtend(self):
        """The layout() method should be called once when a boxlist is extended
        with a sequence of boxes and items."""
            
        s = (Box(),Box(),Box(),Box())    
        self.l.extend(s)
        self.assertEqual(self.l.log,1)
        
    def testDel(self):
        """The layout() method should be called once when a box is deleted from
        a boxlist."""
            
        del self.l[1]
        self.assertEqual(self.l.log,1)
            
    def testPop(self):
        """The layout() method should be called once when a box is popped from a 
        boxlist."""
        
        self.l.pop()
        self.assertEqual(self.l.log,1)
        self.l.pop(0)
        self.assertEqual(self.l.log,2)
        
    def testSort(self):
        """The layout() method should be called once when a boxlist is
        sorted."""
        
        self.l.sort()
        self.assertEqual(self.l.log,1)
        
    def testReverse(self):
        """The layout() method should be called once when a boxlist is
        reversed."""
        
        self.l.reverse()
        self.assertEqual(self.l.log,1)
    
    def testRemove(self):
        """The layout() method should be called once when a box is deleted from
        a boxlist with the remove method."""
        
        self.l.remove(self.c)
        self.assertEqual(self.l.log,1)
        self.l.remove(self.a)
        self.assertEqual(self.l.log,2)

    def testSet(self):
        """The layout() method should be called once when a box is replaced in a
        boxlist."""
        
        self.l[1] = Box()
        self.assertEqual(self.l.log,1)

if __name__ == '__main__':
    unittest.main()