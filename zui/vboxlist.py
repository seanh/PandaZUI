from boxlist import BoxList
from pandac.PandaModules import *

class VBoxList(BoxList):

    def __init__(self,margin=0.1):
        BoxList.__init__(self)
        self.margin = margin
        
    def layout(self):
        """Arrange all of the boxes in this boxlist in a vertical line."""

        for box in self.boxes:
            i = self.boxes.index(box)
            if i == 0:
                # This is the first box in this boxlist. Align it with the
                # top-left of this boxlist.
                x = self.getX()
                y = self.getZ()
                margin = 0
            else:
                # Align `box` with the box before it in this boxlist.
                before = self.boxes[i-1]
                bottom_left,top_right = before.getTightBounds()
                x = bottom_left.getX()
                y = bottom_left.getZ()
                margin = self.margin
            
            # Align the left side of `box` with x.
            bottom_left,top_right = box.getTightBounds()        
            left = bottom_left.getX()
            distance = x - left
            box.setPos(box.getPos() + Vec3(distance,0,0))
        
            # Align the top side of `box` with y.
            top = top_right.getZ()
            distance = y - top
            box.setPos(box.getPos() + Vec3(0,0,distance))

            # Move `box` down by a distance of `margin`.        
            box.setPos(box.getPos() + Vec3(0,0,-margin))
