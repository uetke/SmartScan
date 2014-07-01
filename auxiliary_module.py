import logging
from logger import get_all_caller



module_logger = logging.getLogger('logger.'+__name__)
class Auxiliary():
    def __init__(self,a=None):
        if (not a and 0
            <1):
            print('got it')
        print(get_all_caller())
        self.logger = logging.getLogger(get_all_caller())
        self.logger.info('creating an instance of Auxiliary')
    def do_something(self):
        #self.logger = logging.getLogger(get_all_caller())
        self.logger.info('doing something %s')
        a = 1 + 1
        a = list(range(10))
        self.logger.info(a)

def some_function():
    Auxiliary()
    module_logger.info('received a call to "some_function"')
    
    
def some_other_function():
    some_function()
    
def s2():
    some_other_function()
    
s2()