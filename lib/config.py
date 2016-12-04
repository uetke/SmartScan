"""
config - loads configuration files
"""

import os.path
import logging
import xml.etree.cElementTree as ET

import ruamel.yaml

from lib.logger import get_all_caller

class DeviceConfig():
    def __init__(self,name=None, type='Adwin', filename='config/config_devices.xml'):
	from lib.xml2dict import xmltodict

        self.logger = logging.getLogger(get_all_caller())
        tree = ET.ElementTree(file=filename)
        self._type = type
        root = tree.getroot()
        if root.find(".//*[@Name='%s']"%name)!= None:
            self.logger.info('Loaded the data for %s in %s' %(name,filename))
            self.properties = xmltodict(root.find(".%s//*[@Name='%s']" %(type,name)))
        elif name==None:
            self.properties = []
            self.logger.info('Loaded all the data from %s' %(filename))
            for tags in root.find(".%s" %type):
                name = tags.get('Name')
                self.properties.append(name)
        else:
            self.logger.error("Name of Device is not in XML-file")

    def __str__(self):
        return '{} Device: {}'.format(self._type, self.properties['Name'])

    def __repr__(self):
        return '<{}>'.format(str(self))

    def __getitem__(self, key):
        return self.properties[key]

# Load the variable definition file

def open_configfile(basename):
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(project_root, 'config')
    full_name = os.path.join(config_dir, basename)
    return open(full_name)

VARIABLES = ruamel.yaml.load(open_configfile('variables.yml'))
CONSTANTS = ruamel.yaml.load(open_configfile('constants.yml'))
