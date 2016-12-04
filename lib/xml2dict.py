import warnings
import copy

def xmltodict(element):
    """converts the XML-file to a dictionary"""
    def xmltodict_handler(parent_element,result={}):
        for element in parent_element:
            if len(element):
                obj = xmltodict_handler(element)
            else:
                obj = copy.copy(element.attrib)
                for i, j in obj.items():
                    if j.isdigit():
                        obj[i] = int(j)
                    else:
                        try:
                            obj[i]=float(j)
                        except:
                            pass
            if result.get(element.tag):
                if hasattr(result[element.tag], "append"):
                    result[element.tag].append(obj)
                else:
                    result[element.tag] = [result[element.tag], obj]
            else:
                result[element.tag] = obj
        return result

    result = copy.copy(element.attrib)
    return xmltodict_handler(element,result)

from .config import DeviceConfig as device
from .config import VARIABLES


class variables:
    """
    Transitional class to support old scripts that need access to variables
    """
    def __init__(self, name, filename=None):
        self.name = name.lower()
        warnings.warn("lib.xmltodict.variables is deprecated. Use the lib.config.VARIABLES dict!",
                      DeprecationWarning)

    @property
    def properties(self):
        return VARIABLES[self.name]


if __name__ == '__main__':
    fifo=VARIABLES['fifo']
    #print(fifo.properties)
    counter = device()
    print(counter.properties)
