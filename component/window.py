from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from component.widget import SpinboxWidget, RadioButtonWidget


class SubWindow(QMainWindow):
    def __init__(self, parent=None, mode=None, message=None, db=None, values=None):
        super(SubWindow, self).__init__(parent)
        self.mode = mode
        self.db = db
        self.width = 240
        self.height = 180
        self.center = QDesktopWidget().availableGeometry().center()
        self.rectangle = self.frameGeometry()

        # 화면 크기, 위치 설정
        self.setGeometry(0, 0, self.width, self.height)
        self.rectangle.moveCenter(self.center)
        self.move(self.rectangle.topLeft())

        if mode in ['worker', 'workshift']:
            # values = (default, min, max, step)
            self.setCentralWidget(SpinboxWidget(self, mode, message, db, values))
        else:
            # values = assistant_mode
            self.setCentralWidget(RadioButtonWidget(self, message, db, values))
