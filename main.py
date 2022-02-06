import sys
from PyQt5.QtWidgets import *

from component.app import WindowApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = WindowApplication()
    window.show()

    sys.exit(app.exec_())
