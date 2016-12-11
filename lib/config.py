"""
config - loads configuration files
"""

import os.path
import logging
import xml.etree.cElementTree as ET

import ruamel.yaml

# Load the variable definition file

def open_configfile(basename):
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(project_root, 'config')
    full_name = os.path.join(config_dir, basename)
    return open(full_name, 'rb')

VARIABLES = ruamel.yaml.safe_load(open_configfile('variables.yml'))
CONSTANTS = ruamel.yaml.safe_load(open_configfile('constants.yml'))

_config_devices_etree = None

# Code to handle device configuration

class DeviceConfig():
    # The argument name 'type' is unfortunate for two reasons:
    # (1) it's a keyword, and
    # (2) the word "Type" is used in a different context in the XML files.
    def __init__(self, name=None, type='Adwin', filename=None, *, type_name=None, force_reload=False):
        from lib.xml2dict import xmltodict
        global _config_devices_etree

        self.logger = logging.getLogger('lib.config.DeviceConfig')

        if filename is None:
            if force_reload or _config_devices_etree is None:
                _config_devices_etree = ET.parse(open_configfile('config_devices.xml'))
            tree = _config_devices_etree
        else:
            tree = ET.parse(filename)

        self._type = type
        root = tree.getroot()

        path = './{type_}/Device'.format(type_=self._type)
        if name is not None:
            path += "[@Name='{name}']".format(name=name)
        if type_name is not None:
            path += "[@Type='{type_name}']".format(type_name=type_name)

        matches = root.findall(path)
        properties = [xmltodict(element) for element in matches]
        if len(properties) == 1:
            self.properties = properties[0]
        elif len(properties) == 0:
            raise ValueError("Device configuration not found: {}".format(path))
        else:
            self.properties = properties

    @staticmethod
    def get_adwin_info(name=None, filename=None):
        if filename is None:
            tree = _config_devices_etree
        else:
            tree = ET.parse(filename)

        root = tree.getroot()
        path = './Adwin'
        if name is not None:
            path += "[@Name='{name}']".format(name=name)

        return root.find(path).attrib

    def __str__(self):
        if isinstance(self.properties, list):
            return 'DeviceConfig for {} {} devices'.format(len(self.properties), self._type)
        else:
            return '{} Device: {}'.format(self._type, self.properties['Name'])

    def __repr__(self):
        return '<{}>'.format(str(self))

    def __getitem__(self, key):
        return self.properties[key]

    def __len__(self):
        if isinstance(self.properties, list):
            return len(self.properties)
        else:
            return 1
