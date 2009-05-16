import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from znode import *
from box import Box
from vboxlist import VBoxList
from hboxlist import HBoxList
from memento import Memento, Originator

from direct.gui.DirectGui import *

def card():
    """Return a geomnode for some storycard-shaped geometry."""
    
    left,right,bottom,top = -3,3,-4,4
    cm = CardMaker('StoryCard')            
    cm.setFrame(left,right,bottom,top)
    return cm.generate()

class StoryCard(ZNode, Highlightable, Draggable):
    """A StoryCard consists of some card-shaped background geometry, and on top
    of that a vbox with a title (DirectLabel), icon (DirectLabel) and main text
    (DirectEntry).Along the bottom of the card is an hbox containing buttons
    that control the card.
    
    A StoryCard has various binary states that can be toggled:
    
    focusable/not-focusable:    whether the card can be focused (zoomed to) by
                                the viewport. Functionality from znode. (Or
                                Focusable mixin class?)
                                
                                card.set_zoomable(True|False)
    
    draggable/not-draggable:    whether the card can be dragged or not,
                                functionality from Draggable mixin class.
                                
                                card.set_draggable(True|False)
                                
    highlightable/not-highlightable:    whether the card responds to mouse-overs
                                        or not, functionality from highlightable
                                        mixin class.
                                        
                                card.set_highlightable(True|False)  
                                        
    high-detail/low-detail: whether the highdetail vbox and hbox are shown or
                            the low detail.
                            
                            card.set_detail("high"|"low")
                            
    editable/not-editable: whether the DirectEntry is active and focussed or
                           not.
                           
                            card.set_editable(True|False)

    show-buttons/don't-show-buttons: whether or not the row of DirectButton's
                                     along the bottom of the card is shown.
                                     
                            card.show_buttons(True|False)
                           
    All of these states must be controlled by user classes, e.g. a StoryCard
    subclass that is a FocusObserver, a StoryMap that owns the StoryCard, or
    some sort of global Controller class.
     
    """
    def __init__(self,function):

        self.function = function
        
        ZNode.__init__(self,geomnode=card(), magnification=.8)        
        self.np.setColor(1,1,1,1)
                
        Draggable.__init__(self)
        Highlightable.__init__(self)

        # Uncomment to apply a texture to the card.
        #tex = loader.loadTexture('card.png')
        #self.np.setTexture(tex)

        # Now to add the DirectGUI widgets onto the card. A StoryCard has two
        # VBoxes containing DirectGUI objects, one that is shown when the card
        # is far from the viewport and displaying itself in low detail, and one
        # that is shown when the viewport is focused on the card and the card is
        # showing itself in high detail.
        self.lowDetailVBox = VBoxList()
        self.highDetailVBox = VBoxList()
        self.lowDetailVBox.reparentTo(self.np)
        self.highDetailVBox.reparentTo(self.np)

        # The title of the function of this card.
        font = 'storymaps/data/TypeWritersSubstitute-Black.ttf'

        title = DirectLabel(text=self.function.name,
                            text_font=loader.loadFont(font),
                            text_bg=(1,1,1,0),
                            frameColor=(1,1,1,1),
                            scale=.7,
                            suppressMouse=0)
        b = Box()
        b.fill(title)                            
        self.lowDetailVBox.append(b)

        title = DirectLabel(text=self.function.name,
                            text_font=loader.loadFont(font),
                            text_bg=(1,1,1,0),
                            frameColor=(1,1,1,1),
                            scale=.7,
                            suppressMouse=0)
        b = Box()
        b.fill(title)                            
        self.highDetailVBox.append(b)

        # The icon of the function of this card. Use Panda's mipmapping
        # to handle scaling the image efficiently.
        tex = loader.loadTexture(function.image)
        tex.setMagfilter(Texture.FTLinearMipmapLinear)
        tex.setMinfilter(Texture.FTLinearMipmapLinear)

        icon = DirectLabel(image=tex)
        icon.setScale(2.5)
        b = Box()
        b.fill(icon)                            
        self.lowDetailVBox.append(b)

        icon = DirectLabel(image=tex)
        b = Box()
        b.fill(icon)                                    
        self.highDetailVBox.append(b)

        # The longer description of the Propp function.
        self.entry  = DirectEntry(initialText=self.function.desc,
                                 text_font=loader.loadFont('storymaps/data/WritersFont.ttf'),
                                 scale=.4,
                                 width=13,
                                 numLines=7,
                                 suppressMouse=0,
                                 frameColor = (1,1,1,1))
        self.entry['state'] = DGG.DISABLED

        b = Box()
        b.setColor(1,1,1,0)
        b.fill(self.entry)                            
        self.highDetailVBox.append(b)

        self.lowDetailVBox.setPos(self.lowDetailVBox.np,-2.6,0,4)
        self.highDetailVBox.setPos(self.lowDetailVBox.getPos())

        self.highDetailVBox.hide()

        # A place for subclasses to put buttons.
        self.buttons = HBoxList()             
        self.buttons.reparentTo(self.np)   
        self.buttons.setScale(.6)
        self.buttons.setPos(-1.8,0,-1.6)
        self.buttons.hide()

        self.disabled = False

    def set_detail(self,detail):        
        if detail == "high":
            self.lowDetailVBox.hide()
            self.highDetailVBox.show()            
        elif detail == "low":
            self.lowDetailVBox.show()
            self.highDetailVBox.hide()
        else:
            raise Exception('Argument to set_detail must be "high" or "low".')

    def set_editable(self,boolean):        
        if boolean:
            self.entry['state'] = DGG.NORMAL
            self.entry['focus'] = 1
        else:
            self.entry['state'] = DGG.DISABLED
            self.entry['focus'] = 0
        
    def show_buttons(self,boolean):    
        if boolean:
            self.buttons.show()
        else:
            self.buttons.hide()

    def disable(self):
        disabled_color = Point4(.5,.5,.5,1)
        self.np.setColor(disabled_color)
        for box in self.lowDetailVBox:
            box.contents.setColor(disabled_color)    
        for box in self.highDetailVBox:
            box.contents.setColor(disabled_color)
        for box in self.buttons:
            box.contents.setColor(disabled_color)
        self.set_highlightable(False)
        self.set_draggable(False)        
        self.disabled = True

    def enable(self):
        color = Point4(1,1,1,1)
        self.np.setColor(color)
        for box in self.lowDetailVBox:
            box.contents.setColor(color)    
        for box in self.highDetailVBox:
            box.contents.setColor(color)
        for box in self.buttons:
            box.contents.setColor(color)
        self.set_highlightable(True)
        self.set_draggable(True)
        self.disabled = False

       
    # Implement the Originator interface of the Memento pattern for saving and
    # restoring user content. 
    class Memento(Memento):
        def __init__(self,function,text,cls,disabled):
            self.function = function
            self.text = text
            self.cls = cls
            self.disabled = disabled
        def __str__(self):
            return '\n\n' + self.function.__str__() + '\n\n' + self.text
    def create_memento(self):
        return StoryCard.Memento(self.function,self.entry.get(),self.__class__,self.disabled)
    def restore_memento(self,memento):    
        self.entry.enterText(memento.text)
        if memento.disabled: self.disable()
            
# FIXME. These are static (class) mixins, the user needs to define new 
# classes for each combination of mixins. We want dynamic mixins instead.                        
class FocusObserverStoryCard(FocusObserver):
    """A mixin class for StoryCard that automatically responds to viewport focus
    changes."""

    def __init__(self):
        FocusObserver.__init__(self)
        self._unfocus()

    def enterNone(self):
        """Viewport focus has changed to None."""
        pass

    def exitNone(self):
        """Undo any changes made by enterNone."""
        pass

    def _focus(self):
        if not self.disabled:
            self.set_editable(True)
            self.set_zoomable(False)
            self.set_draggable(False)
            self.set_highlightable(False)
        self.show_buttons(True)
        self.set_detail("high")
    
    def _unfocus(self):
        if not self.disabled:
            self.set_editable(False)
            self.set_zoomable(True)
            self.set_draggable(True)
            self.set_highlightable(True)
        self.show_buttons(False)
        self.set_detail("low")

    def enterSelf(self):
        """Viewport focus has changed to this znode."""
        self._focus()
        
    def exitSelf(self):
        """Undo any changes made by enterSelf."""
        self._unfocus()

    def enterParent(self):
        """Viewport focus has changed to the zparent of this znode."""
        pass
        
    def exitParent(self):
        """Undo any changes made by enterParent."""
        pass
        
    def enterSibling(self):
        """Viewport focus has changed to a sibling znode of this znode."""
        self.set_draggable(False)
        
    def exitSibling(self):
        """Undo any changes made by enterSibling."""
        self.set_draggable(True)

    def enterOther(self):
        """Viewport focus has changed to some other znode."""
        pass
        
    def exitOther(self):
        """Undo any changes made by enterOther."""
        pass
        
class ChoosableStoryCard:
    """A mixin class for StoryCard that adds an 'Add' button.
    
    Messages sent by ChoosableStoryCard:
    
    add --  the add button on this story card was pressed.
    
            arg: this story card.
            
    """
    def __init__(self):

        icon = loader.loadTexture('storymaps/data/actions/add.svg.png')
        icon.setMagfilter(Texture.FTLinearMipmapLinear)
        icon.setMinfilter(Texture.FTLinearMipmapLinear)
        rollover_icon = loader.loadTexture('storymaps/data/actions/add_rollover.svg.png')
        rollover_icon.setMagfilter(Texture.FTLinearMipmapLinear)
        rollover_icon.setMinfilter(Texture.FTLinearMipmapLinear)
        self.addButton = DirectButton(image= (icon, rollover_icon, rollover_icon, icon), command = self.add, suppressMouse=0)
        b = Box()
        b.fill(self.addButton)              
        self.buttons.append(b)
        self.addButton['state'] = DGG.NORMAL

    def add(self):
        messager.send('add',self)

    def disable(self):
        StoryCard.disable(self)
        self.addButton['state'] = DGG.DISABLED

    def enable(self):
        StoryCard.enable(self)
        self.addButton['state'] = DGG.NORMAL

    # ChoosableStoryCard's are not editable.
    # FIXME: this is not really an ideal thing to do with mixin classes because
    # it means that ChoosableStoryCard has to be inherited before StoryCard or
    # the method won't be overridden.
    def set_editable(self,boolean):        
        pass

class EditableStoryCard:
    """A mixin class for StoryCard that adds editable text, and copy, paste and
    remove buttons.
    
    Messages sent by EditableStoryCard:
    
    remove  -- the remove button on this card was pressed.
    
                arg: this card.
                
    copy    -- the copy button on this card was pressed.
    
               arg: the text that was copied, that is to go into the clipboard.
               
    paste   -- the paste button on this card was pressed.
    
               arg: a function that can be called with a single string as
                    argument to paste the string into this card.
                    
    """
    
    # The clipboard is just a class variable. Clipboard funcionality would be
    # more extensible and could be used by any class if it were implemented as
    # a global singleton Clipboard object.
    clipboard = ""
    
    def __init__(self):

        f = 'storymaps/data/actions/copy.svg.png'
        icon = loader.loadTexture(f)
        icon.setMagfilter(Texture.FTLinearMipmapLinear)
        icon.setMinfilter(Texture.FTLinearMipmapLinear)
        f = 'storymaps/data/actions/copy_rollover.svg.png'
        rollover_icon = loader.loadTexture(f)
        rollover_icon.setMagfilter(Texture.FTLinearMipmapLinear)
        rollover_icon.setMinfilter(Texture.FTLinearMipmapLinear)
        copyButton = DirectButton(image=(icon, rollover_icon,
                                         rollover_icon, icon),
                                  command=self.copy,suppressMouse=0)
        b = Box()
        b.fill(copyButton)                            
        self.buttons.append(b)

        f = 'storymaps/data/actions/paste.svg.png'
        icon = loader.loadTexture(f)
        icon.setMagfilter(Texture.FTLinearMipmapLinear)
        icon.setMinfilter(Texture.FTLinearMipmapLinear)
        f = 'storymaps/data/actions/paste_rollover.svg.png'
        rollover_icon = loader.loadTexture(f)
        rollover_icon.setMagfilter(Texture.FTLinearMipmapLinear)
        rollover_icon.setMinfilter(Texture.FTLinearMipmapLinear)
        pasteButton = DirectButton(image=(icon, rollover_icon,
                                          rollover_icon, icon),
                                   command=self.paste,suppressMouse=0)
        b = Box()
        b.fill(pasteButton)                            
        self.buttons.append(b)

        f = 'storymaps/data/actions/remove.svg.png'
        icon = loader.loadTexture(f)
        icon.setMagfilter(Texture.FTLinearMipmapLinear)
        icon.setMinfilter(Texture.FTLinearMipmapLinear)
        f = 'storymaps/data/actions/remove_rollover.svg.png'
        rollover_icon = loader.loadTexture(f)
        rollover_icon.setMagfilter(Texture.FTLinearMipmapLinear)
        rollover_icon.setMinfilter(Texture.FTLinearMipmapLinear)
        removeButton = DirectButton(image=(icon, rollover_icon,
                                           rollover_icon, icon),
                                    command=self.remove, suppressMouse=0)
        b = Box()
        b.fill(removeButton)                            
        self.buttons.append(b)        

    def remove(self):
        messager.send('remove',self)

    # FIXME: should we be using the general messager interface for copy and
    # paste? These aren't really broadcast messages, there only needs to be one
    # singleton clipboard object that receives these messages. When a message
    # is going to one object, just call a method, when it's going to many
    # broadcast a message.
    def copy(self):
        EditableStoryCard.clipboard = self.entry.get()

    def paste(self):
        self.insert(EditableStoryCard.clipboard)

    def insert(self,text):
        """Insert the given text at the given cursor position."""
        c = self.entry.guiItem.getCursorPosition()
        t = self.entry.get()[:c] + text + self.entry.get()[c:]
        self.entry.enterText(t)

# Class that just combine different combinations of mixins with StoryCard.
# (If we used dynamic mixins we wouldn't need to do this.)        
class FocusableChoosableStoryCard(ChoosableStoryCard, StoryCard, FocusObserverStoryCard):

    def __init__(self,function):
        StoryCard.__init__(self,function)
        ChoosableStoryCard.__init__(self)
        FocusObserverStoryCard.__init__(self)

class FocusableEditableStoryCard(StoryCard, FocusObserverStoryCard, EditableStoryCard):

    def __init__(self,function):
        StoryCard.__init__(self,function)
        FocusObserverStoryCard.__init__(self)
        EditableStoryCard.__init__(self)        