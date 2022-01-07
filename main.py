import sys
from PyQt5.QtWidgets import *

from db import DataBase
from component.app import WindowApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    database = DataBase()
    database.db = 'test.db'     # TODO: db명 환경변수로 분리

    window = WindowApplication(db=database)
    window.show()

    sys.exit(app.exec_())
