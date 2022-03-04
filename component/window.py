from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QWidget

from component.widget import RadioButtonWidget, FileWidget, OptionWidget

window_title_dict = {
        "config": {
            "worker": "시간당 근무 인원수",
            "assistant": "사수/부사수 모드",
            "work_shift": "근무교대"
        },
        "db": {
            "register": "파일 등록하기",
            "edit": "데이터 수정하기",
            "add": "데이터 추가하기",
            "delete": "데이터 삭제하기"
        },
        "option": {
            "outside": "영외 인원 등록하기",
            "exception": "열외 인원 등록하기",
            "special_relation": "예외 관계 설정하기"
        }
    }


class MenuWindow(QMainWindow):
    def __init__(self, parent: QMainWindow, width: int, height: int):
        super(MenuWindow, self).__init__(parent)

        self.width = width
        self.height = height

        self.setWidgetPosition()

    def __call__(self, typeof_widget, mode):
        self.setWindowTitle(window_title_dict[typeof_widget][mode])
        if typeof_widget == "config":
            widget = RadioButtonWidget.init_widget(mode=mode)
        elif typeof_widget == "db":
            widget = FileWidget.init_db_widget(mode=mode)
        elif typeof_widget == "option":
            widget = OptionWidget.init_option_widget(mode=mode)
        else:
            return

        if isinstance(widget, QWidget) is False:
            return False

        self.setCentralWidget(widget)
        return True

    def setWidgetPosition(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

    @classmethod
    def menu_window(cls, w, typeof_widget, mode, width, height):
        _window = cls(w, width, height)

        success = _window(typeof_widget, mode)
        return _window if success else None
