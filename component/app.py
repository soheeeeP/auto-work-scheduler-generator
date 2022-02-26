from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QPushButton, QDateEdit, QCalendarWidget, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QWidget, QLabel, QListWidget, QListWidgetItem, QGroupBox

from component.window import MenuWindow
from component.dialog import LogInDialog
from settings import login

from scheduler import AdjustedWorkSchedulerGenerator


class WindowApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        dialog = LogInDialog()
        dialog.exec_()

        login(dialog.login_user_data)

        self.width = 540
        self.height = 360

        today = QDate.currentDate()

        self.calendar = today
        self.start_date = today
        self.end_date = today.addDays(7)
        self.holiday_list = today

        self.add_button = '추가'
        self.del_button = '삭제'
        self.scheduler = '근무표 생성하기'

        self.start_label = QLabel('시작일')
        self.end_label = QLabel('종료일')
        self.holiday_label = QLabel('휴일')

        self.setupMainWindow()

        self.show()

    @property
    def calendar(self):
        return self._calendar

    @calendar.setter
    def calendar(self, value):
        self._calendar = QCalendarWidget()
        self._calendar.setVerticalHeaderFormat(0)
        self._calendar.setDateRange(value, value.addMonths(1))
        self._calendar.clicked.connect(self.show_selected_date)

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = QDateEdit()
        self._start_date.setDate(value)

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = QDateEdit()
        self._end_date.setDate(value)

    @property
    def holiday_list(self):
        return self._holiday_list

    @holiday_list.setter
    def holiday_list(self, value):
        self._holiday_list = QListWidget()

        for i in range(1, 8):
            day = value.addDays(i)
            if day.dayOfWeek() == 6 or day.dayOfWeek() == 7:
                item = QListWidgetItem()

                holiday = QDateEdit()
                holiday.setDate(day)

                self._holiday_list.addItem(item)
                self._holiday_list.setItemWidget(item, holiday)

    @property
    def add_button(self):
        return self._add_button

    @add_button.setter
    def add_button(self, value):
        self._add_button = QPushButton(value)
        self._add_button.clicked.connect(self.add_holiday_to_list)

    @property
    def del_button(self):
        return self._del_button

    @del_button.setter
    def del_button(self, value):
        self._del_button = QPushButton(value)
        self._del_button.clicked.connect(self.delete_holiday_from_list)

    @property
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value):
        self._scheduler = QPushButton(value)
        self._scheduler.clicked.connect(self.create_schedule)

    def setupMenuBar(self):
        menu_bar = self.menuBar()

        setting_menu = menu_bar.addMenu("설정")

        workerPerTimeMenu = QAction("시간당 근무 인원수 설정", self)
        setting_menu.addAction(workerPerTimeMenu)
        workerPerTimeMenu.triggered.connect(self.workerPerTerm)

        assistantModeMenu = QAction("사수/부사수 옵션 설정", self)
        setting_menu.addAction(assistantModeMenu)
        assistantModeMenu.triggered.connect(self.assistantMode)

        workShiftTermMenu = QAction("근무교대 텀 설정", self)
        setting_menu.addAction(workShiftTermMenu)
        workShiftTermMenu.triggered.connect(self.workShiftTerm)

        db_menu = menu_bar.addMenu("DB 생성/조회")

        registerDBMenu = QAction("인원DB 등록", self)
        db_menu.addAction(registerDBMenu)
        registerDBMenu.triggered.connect(self.registerDB)

        editviewDBMenu = QAction("인원DB 수정 및 조회", self)
        db_menu.addAction(editviewDBMenu)
        editviewDBMenu.triggered.connect(self.editDB)

        deleteDBMenu = QAction("인원DB 삭제", self)
        db_menu.addAction(deleteDBMenu)
        deleteDBMenu.triggered.connect(self.deleteDB)

        option_menu = menu_bar.addMenu("추가사항")

        outsideTheBarrackMenu = QAction("영외인원 등록 및 수정", self)
        option_menu.addAction(outsideTheBarrackMenu)
        outsideTheBarrackMenu.triggered.connect(self.outsideOption)

        exceptionMenu = QAction("열외인원 등록 및 수정", self)
        option_menu.addAction(exceptionMenu)
        exceptionMenu.triggered.connect(self.exceptionOption)

        specialRelationMenu = QAction("특수관계 등록 및 수정", self)
        option_menu.addAction(specialRelationMenu)
        specialRelationMenu.triggered.connect(self.specialRelationOption)

        save_menu = menu_bar.addMenu("저장")

        saveWorkRoutineCellMenu = QAction("근무표 저장", self)
        saveWorkCountCellMenu = QAction("근무카운트 저장", self)

        save_menu.addAction(saveWorkRoutineCellMenu)
        save_menu.addAction(saveWorkCountCellMenu)

    def setupMainWindow(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

        self.setWindowTitle('Auto work-scheduler generator for Army Soldiers')

        self.setupMenuBar()

        self.setupLayout()

    def setupLayout(self):
        calendar = QGridLayout()
        calendar.addWidget(self.calendar)

        date = QGridLayout()
        date.addWidget(self.start_label, 0, 0, 1, 2)
        date.addWidget(self.start_date, 0, 2, 1, 2)

        date.addWidget(self.end_label, 1, 0, 1, 2)
        date.addWidget(self.end_date, 1, 2, 1, 2)

        date.addWidget(self.holiday_label, 2, 0, 4, 1)
        date.addWidget(self.add_button, 3, 1, 1, 1)
        date.addWidget(self.del_button, 4, 1, 1, 1)
        date.addWidget(self.holiday_list, 2, 2, 4, 2)

        button = QHBoxLayout()
        button.addWidget(self.scheduler)

        setting_layout = QVBoxLayout()
        setting_layout.addStretch(2)
        setting_layout.addLayout(calendar)
        setting_layout.addStretch(2)
        setting_layout.addLayout(date)
        setting_layout.addStretch(2)
        setting_layout.addLayout(button)
        setting_layout.addStretch(2)

        group = QGroupBox()
        group.setMinimumWidth(360)

        scheduler_box = QVBoxLayout()
        group.setLayout(scheduler_box)

        result_layout = QVBoxLayout()
        result_layout.addWidget(group)

        layout = QHBoxLayout()
        layout.addStretch(2)
        layout.addLayout(setting_layout)
        layout.addStretch(2)
        layout.addLayout(result_layout)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def show_selected_date(self):
        self.calendar.showSelectedDate()

    def add_holiday_to_list(self):
        item = QListWidgetItem()

        new_date = QDateEdit()
        new_date.setDate(QDate.currentDate())

        self.holiday_list.addItem(item)
        self.holiday_list.setItemWidget(item, new_date)

    def delete_holiday_from_list(self):
        item = self.holiday_list.selectedItems()
        self.holiday_list.takeItem(self.holiday_list.row(item[0]))

    def create_schedule(self):
        ymd_format = 'yyyy/MM/dd'

        start = self.start_date.date()
        end = self.end_date.date()

        s_m, s_d = start.month(), start.day()
        base_date = start.toString(ymd_format)

        days_cnt = start.daysTo(end)
        days_on_off = [1 for i in range(days_cnt + 1)]

        for i in range(self.holiday_list.count()):
            item = self.holiday_list.item(i)

            holiday = self.holiday_list.itemWidget(item).date()
            h_m, h_d = holiday.month(), holiday.day()

            days_on_off[(h_m - s_m) * 30 + (h_d - s_d)] = 0

        weekday = AdjustedWorkSchedulerGenerator.init_scheduler(
            base_date=base_date,
            days_on_off=days_on_off,
            day_key="weekday"
        )
        holiday = AdjustedWorkSchedulerGenerator.init_scheduler(
            base_date=base_date,
            days_on_off=days_on_off,
            day_key="holiday"
        )

        print(weekday)
        print(holiday)

        schedule = {start.addDays(i).toString(ymd_format): [] for i in range(1, days_cnt + 1)}
        w_loc, h_loc = 0, 0
        for i, val in enumerate(days_on_off):
            cur_date = start.addDays(i).toString(ymd_format)
            if val == 1:
                schedule[cur_date] = weekday[w_loc]
                w_loc += 1
            else:
                schedule[cur_date] = holiday[h_loc]
                h_loc += 1

        _schedule = {k: v for k, v in sorted(schedule.items(), key=lambda x: x[0])}
        _workers = {}
        term_count = len(list(_schedule.values())[0])
        for users in list(_schedule.values()):
            for i in range(term_count):
                _workers.update(users[i])

        print(_schedule)
        print(_workers)

    def workerPerTerm(self):
        MenuWindow.menu_window(self, 'config', 'worker', 240, 180).show()

    def assistantMode(self):
        MenuWindow.menu_window(self, 'config', 'assistant', 240, 180).show()

    def workShiftTerm(self):
        MenuWindow.menu_window(self, 'config', 'work_shift', 240, 180).show()

    def registerDB(self):
        MenuWindow.menu_window(self, 'db', 'register', 480, 640).show()

    def editDB(self):
        MenuWindow.menu_window(self, 'db', 'edit/view', 480, 640).show()

    def deleteDB(self):
        MenuWindow.menu_window(self, 'db', 'delete', 480, 640).show()

    def outsideOption(self):
        MenuWindow.menu_window(self, 'option', 'outside', 480, 360).show()

    def exceptionOption(self):
        MenuWindow.menu_window(self, 'option', 'exception', 480, 360).show()

    def specialRelationOption(self):
        window = MenuWindow.menu_window(self, 'option', 'special_relation', 480, 360)
        if window:
            window.show()
