from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QPushButton, QDateEdit, QCalendarWidget, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QListWidget, QListWidgetItem, QGroupBox, \
    QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox

from component.window import MenuWindow
from component.message import *
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
        self.scheduler_button = '근무표 생성'
        self.save_button = '근무표 저장'
        self.adjust_button = '근무표 조정'

        self.start_label = QLabel('시작일')
        self.end_label = QLabel('종료일')
        self.holiday_label = QLabel('휴일')

        self._time_labels = None
        self.schedule = None
        self.workers = None
        self.schedule_table = None

        self.scheduler_box = QVBoxLayout()

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
        self._start_date.dateChanged.connect(self.reset_start_date)

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = QDateEdit()
        self._end_date.setDate(value)
        self._end_date.dateChanged.connect(self.reset_end_date)

    @property
    def holiday_list(self):
        return self._holiday_list

    @holiday_list.setter
    def holiday_list(self, value):
        self._holiday_list = QListWidget()
        self.reset_holiday_list(
            start=value,
            days_cnt=7
        )

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
    def scheduler_button(self):
        return self._scheduler_button

    @scheduler_button.setter
    def scheduler_button(self, value):
        self._scheduler_button = QPushButton(value)
        self._scheduler_button.clicked.connect(self.create_schedule)

    @property
    def save_button(self):
        return self._save_button

    @save_button.setter
    def save_button(self, value):
        self._save_button = QPushButton(value)

    @property
    def adjust_button(self):
        return self._adjust_button

    @adjust_button.setter
    def adjust_button(self, value):
        self._adjust_button = QPushButton(value)
        self._adjust_button.clicked.connect(self.adjust_schedule)

    @property
    def time_labels(self):
        return self._time_labels

    @time_labels.setter
    def time_labels(self, term_count):
        self._time_labels = []

        for i in range(term_count):
            s_hour, h_hour = (24 // term_count) * i, (24 // term_count) * (i + 1)
            self._time_labels.append('{0:0>2}:00~{1:0>2}:00'.format(s_hour, h_hour))

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

        db_menu = menu_bar.addMenu("데이터 관리")

        registerDBMenu = QAction("인원 등록", self)
        db_menu.addAction(registerDBMenu)
        registerDBMenu.triggered.connect(self.registerDB)

        addRowDBMenu = QAction("인원 추가", self)
        db_menu.addAction(addRowDBMenu)
        addRowDBMenu.triggered.connect(self.addRowDB)

        editviewDBMenu = QAction("인원 수정", self)
        db_menu.addAction(editviewDBMenu)
        editviewDBMenu.triggered.connect(self.editDB)

        deleteDBMenu = QAction("인원 삭제", self)
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

    def setupMainWindow(self):
        self.setWidgetPosition()

        self.setWindowTitle('Auto work-scheduler generator for Army Soldiers')
        self.setupMenuBar()

        self.setupLayout()

    def setWidgetPosition(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

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
        button.addWidget(self.scheduler_button)

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
        group.setLayout(self.scheduler_box)

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

    def reset_date_range(self, start, end):
        self.calendar.setDateRange(start, end)

    def reset_start_date(self):
        start = self.start_date.date()
        end = self.end_date.date()

        day_diff = start.daysTo(end)

        if day_diff < 0:
            self.start_date.setDate(end.addDays(-1))
            return setWarningMessageBox(self, "종료일을 시작일보다 작게 설정할 수 없습니다.")

        self.reset_date_range(start, end)
        self.reset_holiday_list(
            start=start,
            days_cnt=day_diff
        )

    def reset_end_date(self):
        start = self.start_date.date()
        end = self.end_date.date()

        day_diff = start.daysTo(end)

        if day_diff < 0:
            self.end_date.setDate(start.addDays(1))
            return setWarningMessageBox(self, "종료일을 시작일보다 작게 설정할 수 없습니다.")

        self.reset_date_range(start, end)
        self.reset_holiday_list(
            start=start,
            days_cnt=day_diff
        )

    def add_holiday_to_list(self):
        item = QListWidgetItem()

        new_date = QDateEdit()
        new_date.setDate(QDate.currentDate())

        self.holiday_list.addItem(item)
        self.holiday_list.setItemWidget(item, new_date)

    def delete_holiday_from_list(self):
        item = self.holiday_list.selectedItems()
        self.holiday_list.takeItem(self.holiday_list.row(item[0]))

    def reset_holiday_list(self, start, days_cnt):
        self.holiday_list.clear()
        for i in range(0, days_cnt):
            day = start.addDays(i)
            if day.dayOfWeek() == 6 or day.dayOfWeek() == 7:
                item = QListWidgetItem()

                holiday = QDateEdit()
                holiday.setDate(day)

                self._holiday_list.addItem(item)
                self._holiday_list.setItemWidget(item, holiday)

    def create_schedule(self):
        ymd_format = 'yyyy/MM/dd'

        start = self.start_date.date()
        end = self.end_date.date()

        base_date = start.toString(ymd_format)

        days_cnt = start.daysTo(end)
        if days_cnt == 0:
            return setWarningMessageBox(self, "시작일과 종료일을 같게 설정할 수 없습니다.")
        elif days_cnt <= 0:
            return setWarningMessageBox(self, "종료일을 시작일보다 작게 설정할 수 없습니다.")

        days_on_off = [1 for i in range(days_cnt + 1)]

        for i in range(self.holiday_list.count()):
            item = self.holiday_list.item(i)

            holiday = self.holiday_list.itemWidget(item).date()
            day_diff = start.daysTo(holiday)
            if day_diff > days_cnt:
                continue

            days_on_off[day_diff] = 0

        weekday, w_work_count = AdjustedWorkSchedulerGenerator.init_scheduler(
            base_date=base_date,
            days_on_off=days_on_off,
            day_key="weekday"
        )
        holiday, h_work_count = AdjustedWorkSchedulerGenerator.init_scheduler(
            base_date=base_date,
            days_on_off=days_on_off,
            day_key="holiday"
        )

        _schedule = {start.addDays(i).toString(ymd_format): [] for i in range(0, days_cnt + 1)}
        w_loc, h_loc = 0, 0
        for i, val in enumerate(days_on_off):
            cur_date = start.addDays(i).toString(ymd_format)
            if val == 1:
                _schedule[cur_date] = weekday[w_loc]
                w_loc += 1
            else:
                _schedule[cur_date] = holiday[h_loc]
                h_loc += 1

        self.schedule = {k: v for k, v in sorted(_schedule.items(), key=lambda x: x[0])}
        self.workers = {user_id: 0 for user_id in set(list(w_work_count.keys()) + list(h_work_count.keys()))}

        for u_id, u_count in w_work_count.items():
            self.workers[u_id] += u_count
        for u_id, u_count in h_work_count.items():
            self.workers[u_id] += u_count

        self.set_schedule_table_layout(days_cnt)
        return True

    def adjust_schedule(self):
        self.schedule_table.setEditTriggers(QAbstractItemView.AllEditTriggers)

    def set_schedule_table_layout(self, days_cnt):
        label_font = QFont()
        label_font.setBold(True)

        day_keys = list(self.schedule.keys())
        term_count = len(list(self.schedule.values())[0])
        workers_cnt = len(list(self.schedule.values())[0][0])
        self.time_labels = term_count

        prev_table = self.schedule_table
        if prev_table:
            self.scheduler_box.removeWidget(prev_table)
            self.scheduler_box.removeWidget(self.save_button)
            self.scheduler_box.removeWidget(self.adjust_button)

        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(days_cnt + 1)
        self.schedule_table.setRowCount(term_count * (1 + workers_cnt))
        self.schedule_table.verticalHeader().hide()
        self.schedule_table.setHorizontalHeaderLabels(day_keys)

        for i, key in enumerate(day_keys):
            users_of_day = self.schedule[key]
            for j in range(term_count):
                users_of_term = list(users_of_day[j].values())
                row_idx = j * (workers_cnt + 1)
                self.schedule_table.setItem(row_idx, i, QTableWidgetItem(self.time_labels[j]))

                self.schedule_table.item(row_idx, i).setFont(label_font)
                self.schedule_table.item(row_idx, i).setTextAlignment(Qt.AlignHCenter)
                for k in range(len(users_of_term)):
                    row_idx += 1
                    self.schedule_table.setItem(row_idx, i, QTableWidgetItem(users_of_term[k]))
                    self.schedule_table.item(row_idx, i).setTextAlignment(Qt.AlignHCenter)

        self.schedule_table.resizeRowsToContents()
        self.schedule_table.resizeColumnsToContents()

        self.schedule_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.scheduler_box.addWidget(self.schedule_table)
        self.scheduler_box.addWidget(self.save_button)
        self.scheduler_box.addWidget(self.adjust_button)

    def workerPerTerm(self):
        MenuWindow.menu_window(self, 'config', 'worker', 240, 120).show()

    def assistantMode(self):
        MenuWindow.menu_window(self, 'config', 'assistant', 240, 120).show()

    def workShiftTerm(self):
        MenuWindow.menu_window(self, 'config', 'work_shift', 240, 120).show()

    def registerDB(self):
        MenuWindow.menu_window(self, 'db', 'register', 480, 320).show()

    def addRowDB(self):
        MenuWindow.menu_window(self, 'db', 'add', 480, 320).show()

    def editDB(self):
        MenuWindow.menu_window(self, 'db', 'edit', 480, 320).show()

    def deleteDB(self):
        MenuWindow.menu_window(self, 'db', 'delete', 480, 320).show()

    def outsideOption(self):
        MenuWindow.menu_window(self, 'option', 'outside', 480, 360).show()

    def exceptionOption(self):
        MenuWindow.menu_window(self, 'option', 'exception', 480, 360).show()

    def specialRelationOption(self):
        window = MenuWindow.menu_window(self, 'option', 'special_relation', 480, 360)
        if window:
            window.show()
