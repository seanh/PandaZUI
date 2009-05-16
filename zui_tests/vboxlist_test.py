import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import *
from vboxlist import *

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

class TestVBoxList(unittest.TestCase):
    """Tests to ensure that boxes added to a VBoxList are positioned correctly.
    """

    def setUp(self):
        self.vbox = VBoxList()
        
    def tearDown(self):
        pass    

    def testAppend(self):
        """Boxes appended to a VBoxList should be positioned in a vertical
        top-to-bottom line with the position of the VBoxList being the top-left
        of the line."""

        for x,y,z in ( (0,0,0), (-1,0,1),(1,0,-1) ):

            self.vbox.setPos(x,y,z)
            
            self.vbox.append(Box())
            # Assume all boxes are the same size.
            bottom_left,top_right = self.vbox[0].getTightBounds()
            height = top_right.getZ() - bottom_left.getZ()
            self.assert_(same(self.vbox[0].left(),x))
            self.assert_(same(self.vbox[0].top(),z))
            
            self.vbox.append(Box())
            self.assert_(same(self.vbox[0].left(),x))
            self.assert_(same(self.vbox[0].top(),z))
            self.assert_(same(self.vbox[1].left(),x))
            self.assert_(same(self.vbox[1].top(),z-height-self.vbox.margin))
            
            self.vbox.append(Box())
            self.assert_(same(self.vbox[0].left(),x))
            self.assert_(same(self.vbox[0].top(),z))
            self.assert_(same(self.vbox[1].left(),x))
            self.assert_(same(self.vbox[1].top(),z-height-self.vbox.margin))
            self.assert_(same(self.vbox[2].left(),x))
            self.assert_(same(self.vbox[2].top(),z-(2*(height+self.vbox.margin))))

if __name__ == '__main__':
    unittest.main()