from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from component.widget import RadioButtonWidget, FileWidget


class SubWindow(QMainWindow):
    def __init__(self, parent=None, mode=None):
        super(SubWindow, self).__init__(parent)

        self.width = 240
        self.height = 180

        self.setupLayout()

        radio_widget = RadioButtonWidget.init_widget(mode=mode)
        self.setCentralWidget(radio_widget)

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)


class DBWindow(QMainWindow):
    def __init__(self, parent=None, mode=None):
        super(DBWindow, self).__init__(parent)

        self.width = 480
        self.height = 640

        self.setupLayout()

        file_widget = FileWidget.init_db_widget(mode=mode)
        self.setCentralWidget(file_widget)

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)
