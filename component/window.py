from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QWidget, QVBoxLayout, QFileDialog

from component.widget import SpinboxWidget, RadioButtonWidget, FileWidget


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


class DBWindow(QMainWindow):
    def __init__(self, parent=None, mode=None, db=None):
        super(DBWindow, self).__init__(parent)
        self.mode = mode
        self.db = db
        self.width = 480
        self.height = 640
        self.center = QDesktopWidget().availableGeometry().center()
        self.rectangle = self.frameGeometry()

        self.setGeometry(0, 0, self.width, self.height)
        self.rectangle.moveCenter(self.center)
        self.move(self.rectangle.topLeft())

        # TODO: file_widget 위치 조정
        file_widget = FileWidget(db=db)
        if self.mode == 'create':
            file_widget.init_widget()
            file_widget.get_csv_file()
            self.setCentralWidget(file_widget)
        else:
            # TODO: db의 데이터 읽어와서 TableWidget에 set ('조회'인 경우 edit 동작을 수행하지 못하도록 설정)
            pass
