import sys
from PyQt5.QtCore import *

from db import DataBase

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    database = DataBase()
    sys.exit(app.exec_())
