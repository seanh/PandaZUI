import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from box import *
from gridboxlist import *

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

class TestGridBoxList(unittest.TestCase):
    """Tests to ensure that boxes added to a GridBoxList are positioned correctly."""

    def setUp(self):
        self.margin = 0.1
        self.grid_box = GridBoxList(columns=3,margin=self.margin)
        
    def tearDown(self):
        pass    

    def testAppend(self):
        """Boxes appended to a GridBoxList should be positioned in a left-right,
        top-bottom grid."""

        for x,y,z in ( (0,0,0), (-1,0,1),(1,0,-1) ):

            self.grid_box.setPos(x,y,z)
            
            for i in range(9):
                self.grid_box.append(Box())
            # Assume all boxes are the same size.
            bottom_left,top_right = self.grid_box[0].getTightBounds()
            width = top_right.getX() - bottom_left.getX()
            height = top_right.getZ() - bottom_left.getZ()
               
            for i in range(3):
                for j in range(3):
                    left = x + j*(width+self.margin)
                    top = z - i*(height+self.margin)
                    self.assert_(same(self.grid_box[(3*i)+j].left(),left))
                    self.assert_(same(self.grid_box[(3*i)+j].top(),top))
                    
if __name__ == '__main__':
    unittest.main()