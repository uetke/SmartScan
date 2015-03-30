# Collection of functions for keeping an electronic lab logbook
import os
import xml.etree.cElementTree as ET

from datetime import datetime

class logbook():
    """ This class includes all the necessary functions for keeping a centralized lab logbook in xml format. 
        The creation of the class takes on argument that is the directory where files are kept. Ideally this would be D:\Data 
        Or the root of the data directory.
    """
    def __init__(self,directory):
        """ Initializes the class by checking if there are existing files or not in the specified directory. 
        """
        self.directory = directory 
        if self.directory[-1] != '/' or self.directory[-1] != '\\':
            self.directory += '/'
            
        self.directory +='logbook/'
        self.book = self.directory+'logbook.xml'
        self.setups = self.directory+'setups.xml'     
        self.users = self.directory+'users.xml'
        
        new_dir = 0
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
            print('The directory %s had to be created.'%(self.directory))
            new_dir = 1
            # Creates an initial entry for the files to have a consistent structure
            
        if new_dir or not (os.path.exists(self.book) or os.path.exists(self.setups) or os.path.exists(self.users)):
            open(self.book,'a').close()
            root = ET.Element('logbook')
            init = ET.SubElement(root,'entry')
            init.set('Date', str(datetime.now().date()))
            time = ET.SubElement(init,'time')
            time.text = str(datetime.now().time())
            user = ET.SubElement(init,'user')
            user.text = 'Init User'
            setup = ET.SubElement(init,'setup')
            setup.text = 'Initial'
            descr = ET.SubElement(init,'description')
            descr.text = 'This is the inauguration of the logbook'
            detector = ET.SubElement(init,'detector')
            detector.text = 'Detector 1'
            variables = ET.SubElement(init,'variables')
            variables.text = 'Stage 1'
            file = ET.SubElement(init, 'file')
            file.text = 'Path/To/File'
            tree = ET.ElementTree(root)
            tree.write(self.book)
            
            open(self.setups,'a').close()
            root = ET.Element("setups")
            init = ET.SubElement(root,'setup')
            init.set('ID', str(0))
            init.set('Date', str(datetime.now().date()))
            name = ET.SubElement(init,'name')
            name.text = 'Initial'
            description = ET.SubElement(init,'description')
            description.text = 'Initial Description'
            file = ET.SubElement(init,'file')
            file.text = 'No File'
            tree = ET.ElementTree(root)
            tree.write(self.setups)
            
            open(self.users,'a').close() 
            root = ET.Element("users")
            user = ET.SubElement(root,'user')
            user.set('Date', str(datetime.now().date()))
            name = ET.SubElement(user,'name')
            name.text = 'Initial User'
            tree = ET.ElementTree(root)
            tree.write(self.users)
            

    def new_setup(self,name,description,file=None):
        """ Method for inserting a new setup in the setups xml file. 
        """
        
        tree = ET.parse(self.setups)
        setups = tree.getroot()
        
        new_setup = ET.Element('setup')
        
        last_id = int(setups[-1].attrib['ID'])
        
        new_setup.set('ID',str(last_id+1))
        new_name = ET.SubElement(new_setup,'name')
        new_name.text = name
        new_description = ET.SubElement(new_setup,'description')
        new_description.text = description
        if file != None or file!= '':
            new_file = ET.SubElement(new_setup,'file')
        else:
            new_file = 'No File'
        new_file.text = file
               

        setups.append(new_setup)
        tree = ET.ElementTree(setups)
        tree.write(self.setups)
        
    def new_user(self,name):
        """ Method for inserting a user to the users xml file. 
        """

        new_user = ET.Element('user')
        new_user.set('Date', str(datetime.now().date()))
        new_name = ET.SubElement(new_user, 'name')
        new_name.text = name
        
        tree = ET.parse(self.users)
        users = tree.getroot()
        users.append(new_user)
        tree = ET.ElementTree(users)
        tree.write(self.users)
        

    def write_entry(self,user,detectors,variables,description,setup,file=None):
        """ Method for adding an entry to the logbook. 
        """
        new_entry = ET.Element('entry')
        new_entry.set('Date',str(datetime.now().date()))
        time = ET.SubElement(new_entry,'time')
        time.text = str(datetime.now().time())
        new_user = ET.SubElement(new_entry,'user')
        new_user.text = user
        new_detectors = ET.SubElement(new_entry,'detectors')
        new_detectors.text = detectors
        new_variables = ET.SubElement(new_entry,'variables')
        new_variables.text = variables
        new_description = ET.SubElement(new_entry,'description')
        new_description.text = description
        new_file = ET.SubElement(new_entry,'file')
        new_file.text = file
        new_setup = ET.SubElement(new_entry,'setup')
        new_setup.text = setup
        
        tree = ET.parse(self.book)
        logbook = tree.getroot()
        logbook.append(new_entry)
        tree = ET.ElementTree(logbook)
        tree.write(self.book)
        
    def get_last_user(self):
        """ Returns the name of the last user who wrote an entry to the logbook. 
        """ 
        tree = ET.parse(self.book)
        entries = tree.getroot()
        last_user = entries[-1].find('user').text
        return last_user
    
    def get_last_setup(self):
        """ Returns the ID and name of the last setup used. 
            Returns a list, the first element is an integer, the second a string.
        """
        tree = ET.parse(self.book)
        entries = tree.getroot()
        last_setup_id = int(entries[-1].find('setup').text)
        
        tree = ET.parse(self.setups)
        setups = tree.getroot()
        last_setup = setups.findall(".//name/..[@ID='%i']"%(last_setup_id))
        last_setup_name = last_setup[0].find('name').text
        return list([last_setup_id, last_setup_name])
        
        
