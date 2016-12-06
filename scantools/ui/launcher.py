"""
scantools.ui.launcher

Start different components of the smartscan suite within one process.
"""

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from ..app import ScanApplication

import sys

class LauncherWindow(QtGui.QMainWindow):
    def __init__(self, parent=None, no_exit=False):
        super().__init__(parent)
        self._no_exit = no_exit

        self._centralWidget = QtGui.QWidget(self)
        self._vlayout = QtGui.QVBoxLayout(self._centralWidget)

        app = ScanApplication()

        self._buttons = []
        for scan_tool in app.scan_tools:
            btn = AppLaunchButon(self, scan_tool, self)
            self._vlayout.addWidget(btn)
            self._buttons.append(btn)

        self.setCentralWidget(self._centralWidget)
        self.setWindowTitle("SmartScan Launcher")

    def closeEvent(self, ce):
        reply = QtGui.QMessageBox.question(self, 'Really Quit?', 
            "Closing this window will close all running tools!\nAre you sure?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            ce.accept()
            if self._no_exit:
                for w in self.children():
                    if isinstance(w, QtGui.QMainWindow):
                        w.close()
            else:
                QtGui.QApplication.quit()
        else:
            ce.ignore()


class AppLaunchButon(QtGui.QPushButton):
    def __init__(self, parent, scan_tool, window):
        super().__init__(parent)
        self._scan_tool = scan_tool
        self._window = window

        txt = QtGui.QTextDocument()
        txt.setHtml("<p align=center><b><big>{}</big></b><br>{}</p>".format(
            self._scan_tool.name, self._scan_tool.description))
        txt.setTextWidth(txt.size().width())
        self._pixmap = QtGui.QPixmap(txt.size().width(), txt.size().height())
        self._pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(self._pixmap)
        txt.drawContents(painter)
        painter.end()
        self._icon = QtGui.QIcon(self._pixmap)

        self.setIconSize(self._pixmap.size())
        self.setIcon(self._icon)

        self.clicked.connect(self._on_clicked)
        self._scan_tool.launched.connect(self._on_launched)
        self._scan_tool.closed.connect(self._on_closed)

    def _on_clicked(self):
        self._scan_tool.launch()

    def _on_launched(self):
        self.setEnabled(False)

    def _on_closed(self):
        self.setEnabled(True)





if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())