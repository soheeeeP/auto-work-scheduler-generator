from PyQt5.QtWidgets import \
    QMainWindow, QDesktopWidget, QAction, QWidget, QSpinBox, \
    QLabel, QVBoxLayout, QPushButton, QRadioButton


# TODO: Window, Menu, Frame 별도의 class로 분리하기
class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self._db = db

        self.width = 720
        self.height = 540
        self.center = QDesktopWidget().availableGeometry().center()
        self.rectangle = self.frameGeometry()

        # 화면 크기, 위치 설정
        self.setGeometry(0, 0, self.width, self.height)
        self.rectangle.moveCenter(self.center)
        self.move(self.rectangle.topLeft())

        self.setWindowTitle('Auto work-scheduler generator for Army Soldiers')

        # 메뉴 생성
        menu_bar = self.menuBar()

        setting_menu = menu_bar.addMenu("설정")

        workerPerTimeMenu = QAction("시간당 근무 인원수 설정", self)
        setting_menu.addAction(workerPerTimeMenu)
        workerPerTimeMenu.triggered.connect(self.worker_per_time_frame)

        assistantModeMenu = QAction("사수/부사수 옵션 설정", self)
        setting_menu.addAction(assistantModeMenu)
        assistantModeMenu.triggered.connect(self.assistant_mode_frame)

        workShiftTermMenu = QAction("근무교대 텀 설정", self)
        setting_menu.addAction(workShiftTermMenu)
        workShiftTermMenu.triggered.connect(self.workshift_term_frame)

        db_menu = menu_bar.addMenu("DB 생성/조회")
        createDBMenu = QAction("인원DB 등록", self)
        editDBMenu = QAction("인원DB 수정", self)
        viewDBMenu = QAction("인원DB 조회", self)
        db_menu.addAction(createDBMenu)
        db_menu.addAction(editDBMenu)
        db_menu.addAction(viewDBMenu)

        option_menu = menu_bar.addMenu("추가사항")
        outsideTheBarrackMenu = QAction("영외인원 등록 및 수정", self)
        exceptionMenu = QAction("열외인원 등록 및 수정", self)
        specialRelationMenu = QAction("특수관계 등록 및 수정", self)

        option_menu.addAction(outsideTheBarrackMenu)
        option_menu.addAction(exceptionMenu)
        option_menu.addAction(specialRelationMenu)

        save_menu = menu_bar.addMenu("저장")
        saveWorkRoutineCellMenu = QAction("근무표 저장", self)
        saveWorkCountCellMenu = QAction("근무카운트 저장", self)

        save_menu.addAction(saveWorkRoutineCellMenu)
        save_menu.addAction(saveWorkCountCellMenu)

        self.show()

    def worker_per_time_frame(self):
        SubWindow(self, 'worker', '시간당 근무 인원수 설정하기\n(0 ~ 3 사이의 수를 입력하세요)', self._db, (self._db.term_count, 0, 3, 1)).show()

    def assistant_mode_frame(self):
        SubWindow(self, 'assistant', '사수/부사수 모드', self._db, None).show()

    def workshift_term_frame(self):
        SubWindow(self, 'workshift', '근무교대 텀 설정하기\n(0 ~ 24 사이의 수를 입력하세요)', self._db, (self._db.worker_per_term, 0, 24, 1)).show()


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

        if mode in ['worker', 'workershift']:
            # values = (default, min, max, step)
            self.setCentralWidget(SpinboxWidget(self, mode, message, db, values))
        else:
            self.setCentralWidget(RadioButtonWidget(self, message, db))


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
    def __init__(self, parent=None, message=None, db=None):
        super(RadioButtonWidget, self).__init__(parent)
        self.db = db
        self.message = message

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
        if self._on_radio_button.isChecked() and self._off_radio_button.isChecked() is False:
            self.db.assistant_mode = True
        elif self._off_radio_button.isChecked() and self._on_radio_button.isChecked() is False:
            self.db.assistant_mode = False
        else:
            raise ValueError('invalid radio input')

    def init_radio_button_frame(self):
        self.on_radio_button = self.message
        self.off_radio_button = self.message
        self._on_radio_button.setChecked(True) if self.db.assistant_mode else self._off_radio_button.setChecked(True)

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

