from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from component.widget import RadioButtonWidget, FileWidget, OptionWidget


class MenuWindow(QMainWindow):
    def __init__(self, parent: QMainWindow, width: int, height: int):
        super(MenuWindow, self).__init__(parent)

        self.width = width
        self.height = height

        self.setupLayout()

    def __call__(self, typeof_widget, mode):
        if typeof_widget == "config":
            widget = RadioButtonWidget.init_widget(mode=mode)
        elif typeof_widget == "db":
            widget = FileWidget.init_db_widget(mode=mode)
        elif typeof_widget == "option":
            widget = OptionWidget.init_option_widget(mode=mode)
        else:
            return

        self.setCentralWidget(widget)

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

    @classmethod
    def menu_window(cls, w, typeof_widget, mode, width, height):
        _window = cls(w, width, height)
        _window(typeof_widget, mode)

        return _window
