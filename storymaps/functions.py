"""This module reads in Propp function data from the functions.xml file and
makes it accessible via a class `Function` and a list of function objects
`functions`."""

from xml.dom import minidom

class Function:
    """
    Simple class to represent a single Propp function.
    
    """        
    def __init__(self,num,name,desc,image):
        self.num = float(num)
        self.name = name
        self.desc = desc
        self.image = image

    def __cmp__(self,other):
        return cmp(self.num,other.num)
    
    def __str__(self):
        """Return the "informal" string representation of this Function. Called
        by str() and print."""
        return self.name + '\n' + self.desc
    
functions = []

xmldoc = minidom.parse('storymaps/data/functions.xml')
for row in xmldoc.getElementsByTagName('row'):
    # Each row corresponds to a Propp function.
    for field in row.getElementsByTagName('field'):
        if field.attributes['name'].value == 'symbol':
            # FIXME: This is not a robust way to access text nodes!
            symbol = field.childNodes[0].data 
        elif field.attributes['name'].value == 'friendly name':
            # FIXME: This is not a robust way to access text nodes!
            name = field.childNodes[0].data
        elif field.attributes['name'].value == 'description':
            # FIXME: This is not a robust way to access text nodes!
            desc = field.childNodes[0].data
        elif field.attributes['name'].value == 'friendly description':
            # FIXME: This is not a robust way to access text nodes!
            friendly_desc = field.childNodes[0].data
    image = 'storymaps/data/'+symbol+'.svg-512.png'
    function = Function(symbol,name,friendly_desc,image)
    functions.append(function)