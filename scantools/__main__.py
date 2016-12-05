import sys

from PyQt4.QtGui import QApplication

from .ui.launcher import LauncherWindow
app = QApplication(sys.argv)
window = LauncherWindow()
window.show()
sys.exit(app.exec_())
