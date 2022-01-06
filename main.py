import sys
from tkinter import *
from PyQt5.QtCore import *

from db import DataBase
from window import Window

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    database = DataBase()
    database.db = 'test.db'     # TODO: db명 환경변수로 분리

    root = Window()
    root.start_window()

    sys.exit(app.exec_())
