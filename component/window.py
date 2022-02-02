from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from component.widget import RadioButtonWidget, FileWidget


class SubWindow(QMainWindow):
    def __init__(self, parent=None, mode=None, db=None, default=None):
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

        if mode == 'worker':
            radio_widget = RadioButtonWidget.worker_widget(db=db, val=default)
        elif mode == 'work_shift':
            radio_widget = RadioButtonWidget.work_shift_widget(db=db, val=default)
        elif mode == 'assistant':
            radio_widget = RadioButtonWidget.assistant_widget(db=db, val=default)
        else:
            return
        self.setCentralWidget(radio_widget)


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
        if mode == 'register':
            file_widget = FileWidget.init_db_register_widget(db=db)
        elif mode == 'edit/view':
            file_widget = FileWidget.init_db_edit_widget(db=db)
        elif mode == 'delete':
            file_widget = FileWidget.init_db_delete_widget(db=db)
        else:
            return
        self.setCentralWidget(file_widget)
