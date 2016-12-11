import logging
import os
import sys
from PyQt4.QtGui import QApplication
from .ui.launcher import LauncherWindow
from lib.logger import logger

project_root = os.path.dirname(os.path.dirname(__file__))
os.chdir(project_root)

# Initialize logging with default settings!
logger('', streamlevel=logging.INFO)

app = QApplication(sys.argv)
window = LauncherWindow()
window.show()
exit_code = app.exec_()
sys.exit(exit_code)
