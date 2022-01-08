from PyQt5.QtWidgets import QWidget, QRadioButton, QPushButton, QVBoxLayout, QSpinBox, QLabel


class SpinboxWidget(QWidget):
    def __init__(self, parent=None, mode=None, message=None, db=None, values=None):
        super(SpinboxWidget, self).__init__(parent)
        self.mode = mode
        self.db = db
        self.message = message
        self.values = values

        self._spinbox = None
        self._label_title = None
        self._button = None

        self.init_widget()

    @property
    def spinbox(self):
        return self._spinbox

    @spinbox.setter
    def spinbox(self, values):
        default_value, min_value, max_value, step = values

        self._spinbox = QSpinBox()
        self._spinbox.setRange(min_value, max_value)
        self._spinbox.setSingleStep(step)
        self._spinbox.setValue(default_value)

    @property
    def label_title(self):
        return self._label_title

    @label_title.setter
    def label_title(self, message):
        self._label_title = QLabel(message)

    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, value):
        self._button = QPushButton(value)

    def save_new_value_in_db(self):
        # todo: term_count와 worker_per_term에 @property 적용하기
        # TODO: db의 값을 수정할때, DROP user TABLE한뒤 다시 CREATE
        if self.mode == 'worker':
            self.db.term_count = self._spinbox.value()
        elif self.mode == 'workshift':
            self.db.worker_per_term = self._spinbox.value()

    def init_widget(self):
        self.spinbox = self.values
        self.label_title = self.message
        self.button = '저장하기'

        self._button.clicked.connect(self.save_new_value_in_db)

        vbox = QVBoxLayout()
        vbox.addWidget(self._label_title)
        vbox.addWidget(self._spinbox)
        vbox.addWidget(self._button)
        vbox.addStretch()

        self.setLayout(vbox)

        # self.setWindowTitle(self.message)
        # TODO: window 위치 조정하기
        self.setGeometry(300, 300, 300, 200)
        self.show()


class RadioButtonWidget(QWidget):
    def __init__(self, parent=None, message=None, db=None, values=None):
        super(RadioButtonWidget, self).__init__(parent)
        self.db = db
        self.message = message
        self.values = values

        self._on_radio_button = None
        self._off_radio_button = None
        self._button = None

        self.init_radio_button_frame()

    @property
    def on_radio_button(self):
        return self._on_radio_button

    @on_radio_button.setter
    def on_radio_button(self, message):
        self._on_radio_button = QRadioButton(f'{message} 설정하기', self)

    @property
    def off_radio_button(self):
        return self._off_radio_button

    @off_radio_button.setter
    def off_radio_button(self, message):
        self._off_radio_button = QRadioButton(f'{message} 해제하기', self)

    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, value):
        self._button = QPushButton(value)

    def save_radio_checked_value_in_db(self):
        # TODO: db의 값을 수정할때, DROP user TABLE한뒤 다시 CREATE
        if self._on_radio_button.isChecked() and self._off_radio_button.isChecked() is False:
            self.db.assistant_mode = True
        elif self._off_radio_button.isChecked() and self._on_radio_button.isChecked() is False:
            self.db.assistant_mode = False
        else:
            raise ValueError('invalid radio input')

    def init_radio_button_frame(self):
        self.on_radio_button = self.message
        self.off_radio_button = self.message
        self._on_radio_button.setChecked(True) if self.values else self._off_radio_button.setChecked(True)

        self.button = '저장하기'
        self._button.clicked.connect(self.save_radio_checked_value_in_db)

        vbox = QVBoxLayout()
        vbox.addWidget(self._on_radio_button)
        vbox.addWidget(self._off_radio_button)
        vbox.addWidget(self._button)
        vbox.addStretch()

        self.setLayout(vbox)

        # TODO: window 위치 조정하기
        self.setGeometry(300, 300, 300, 200)
        self.show()
