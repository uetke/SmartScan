import os
import sys
from PyQt4.QtGui import QApplication
from .ui.launcher import LauncherWindow

project_root = os.path.dirname(os.path.dirname(__file__))
os.chdir(project_root)

app = QApplication(sys.argv)
window = LauncherWindow(no_exit=('--no-exit' in sys.argv))
window.show()
sys.exit(app.exec_())
