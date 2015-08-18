""" Class to make it easy to retrieve the ID from a database. 
"""

from PyQt4.Qt import QComboBox

class new_comboBox(QComboBox):
    def __init__(self,*args):
        super(new_comboBox,self).__init__()
#         QComboBox.__init__(*args)
        self.indexes = []
        
    def addList(self,items):
        """ Increases the default way of adding items. 
            Keeps track of an additional value besides the name. 
        """
        for item in items:
            self.addItem(item[1])
            self.indexes.append(item[0])
            
    def getKey(self):
        """ Returns the Key value of the selected option in the comboBox. 
        """
        return self.indexes[self.currentIndex()]