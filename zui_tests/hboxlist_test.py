import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import *
from hboxlist import *

from pandac.PandaModules import *
import unittest

def same(x,y):
    """NodePath.getTightBounds() doesn't seem to return exactly precise results,
    so this method does a float equality comparison with a degree of tolerance.
    """
    print x,y
    if abs(x-y) < 0.000001:
        return True
    else:
        return False

class TestHBoxList(unittest.TestCase):
    """Tests to ensure that boxes added to an HBoxList are positioned correctly.
    """

    def setUp(self):
        self.hbox = HBoxList()
        
    def tearDown(self):
        pass    

    def testAppend(self):
        """Boxes append to an HBoxList should be positioned in a horizontal
        left-to-right line with the position of the HBoxList being the top-left
        of the line."""

        for x,y,z in ( (0,0,0), (-1,0,1),(1,0,-1) ):

            self.hbox.setPos(x,y,z)
            
            self.hbox.append(Box())
            # Assume all boxes are the same size.
            bottom_left,top_right = self.hbox[0].getTightBounds()
            width = top_right.getX() - bottom_left.getX()
            self.assert_(same(self.hbox[0].left(),x))
            self.assert_(same(self.hbox[0].top(),z))
            
            self.hbox.append(Box())
            self.assert_(same(self.hbox[0].left(),x))
            self.assert_(same(self.hbox[0].top(),z))
            self.assert_(same(self.hbox[1].left(),x+width+self.hbox.margin))
            self.assert_(same(self.hbox[1].top(),z))
            
            self.hbox.append(Box())
            self.assert_(same(self.hbox[0].left(),x))
            self.assert_(same(self.hbox[0].top(),z))
            self.assert_(same(self.hbox[1].left(),x+width+self.hbox.margin))
            self.assert_(same(self.hbox[1].top(),z))
            self.assert_(same(self.hbox[2].left(),x+(2*(width+self.hbox.margin))))
            self.assert_(same(self.hbox[2].top(),z))

if __name__ == '__main__':
    unittest.main()