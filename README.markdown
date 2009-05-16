A ZUI (Zooming User Interface) framework for 
[Panda3D](http://www.panda3d.org/). Requires Panda3D to be installed onyour 
system.

# Features

A ZUI (Zoomable User Interface) is "a graphical environment where users can 
change the scale of the viewed area in order to see more detail or less." The 
idea is that your "desktop" is an infinite and infinitely scalable plane, onto 
which you place all the objects that the user interacts with. Users can pan the 
camera around and zoom it in and out, move the objects around, and generally do 
whatever you can imagine and then implement. I think the main reference for the 
idea has to be the "Zoom World" in Jef Raskin's book _The Humane Interface_, 
but it was never implemented. With all these new devices with small screens the 
I think concept is having a bit of a revival. A few links on the subject:

http://en.wikipedia.org/wiki/Zooming_user_interface
http://advogato.org/article/788.html
http://rchi.raskincenter.org/index.php?title=ZUI_Specification

Some other implementations of this sort of thing include Piccolo, Clutter and 
Project Scene Graph.

http://www.cs.umd.edu/hcil/jazz/
http://clutter-project.org/
https://scenegraph.dev.java.net/

What does this code actually do? Let's see, we've got:

* A ZCanvas, an infinite and infinitely scalable plane with a viewport that can 
pan around and zoom in and out. It's implemented by transforming a node on 
Panda's 2D scene graph. Thanks to ynjh_jo for the code for the zoom 
transformation.

* Nodes that you can automatically zoom the camera to, e.g. by clicking on them

* Nodes can change state depending on what the camera is focused on

* Nodes that respond to mouse-over highlights

* Nodes that can be dragged and dropped onto other nodes

* Container nodes that implement layouts. Provided are horizontal and vertical 
line layouts and a grid layout, but the general Box and BoxList framework 
provided supports easily creating arbitrary layouts. Compound layouts (layouts 
within layouts) are also supported.

* DirectGUI compatibility, i.e. you can embed DirectGUI widgets into the zoom 
scene, and put them into layout containers.

It's all fairly generic, I think, so you could use it to implement lots of 
different interfaces. I'm using it to implement a little story writing 
prototype called 'Story Cards' which is also included in the download.

The code was originally posted to [a thread on the Panda3D 
forums](http://www.panda3d.org/phpbb2/viewtopic.php?t=4604&highlight=).

# Instructions

`zui/` contains the framework itself.

`zui_tests/` contains unit tests for the code in `zui/`.

`zui_demos/` contains unit demos for the code in `zui/`.

`storymaps/` contains a demo application.

`storymaps_demos/` contains unit demos for the code in `storymaps/`.

Code should be run from the top-level folder, e.g.:

    python storymaps/story.py
    
or

    python zui_demos/box_demo.py    
