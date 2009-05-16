from boxlist import BoxList
from pandac.PandaModules import *

class GridBoxList(BoxList):

    def __init__(self,columns,margin=0.1):
    
        BoxList.__init__(self)
        self.columns = columns
        self.margin = margin

    def layout(self):
        """Arrange all of the boxes in this boxlist into a regular grid."""
                
        for offset,box in enumerate(self.boxes):
            
            if offset%self.columns == 0:
                # Align the left of `box` the the X pos of this listbox.
                x = self.getX()
                xmargin = 0
            else:
                # Align the left of `box` with the right of the previous `box`.
                x = self.boxes[offset-1].right()
                xmargin = self.margin
            if offset < self.columns:
                # Align the top of `box` the the Z pos of this listbox.
                z = self.getZ()
                zmargin = 0
            else:
                # Align the top of `box` with the bottom of box above it.
                z = self.boxes[offset-self.columns].bottom()
                zmargin = self.margin

            # Align the left side of `box` with x.
            bottom_left,top_right = box.getTightBounds()        
            left = bottom_left.getX()
            distance = x - left
            box.setPos(box.getPos() + Vec3(distance,0,0))
        
            # Align the top side of `box` with z.
            top = top_right.getZ()
            distance = z - top
            box.setPos(box.getPos() + Vec3(0,0,distance))

            # Move `box` right by a distance of `xmargin`.        
            box.setPos(box.getPos() + Vec3(xmargin,0,0))

            # Move `box` down by a distance of `zmargin`.        
            box.setPos(box.getPos() - Vec3(0,0,zmargin))
    