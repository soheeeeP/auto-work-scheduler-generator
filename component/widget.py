import csv
import pandas as pd
import pathlib

from PyQt5.QtCore import Qt, QDate, QTime, QPropertyAnimation, QSize, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QRadioButton, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, \
    QTableWidget, QTableWidgetItem, QLineEdit, QGridLayout, QTreeWidget, QTreeWidgetItem, \
    QHeaderView, QDateEdit, QTimeEdit, QAbstractItemView, QSizePolicy, QCheckBox, QDesktopWidget

from db import database
from component.dialog import AdminDialog
from component.message import *
import settings


class RadioButtonWidget(QWidget):
    db = database

    message_dict = {
        "worker": "시간당 근무 인원수",
        "work_shift": "근무 교대",
        "assistant": "사수 / 부사수 모드"
    }

    def __init__(self, parent=None):
        super(RadioButtonWidget, self).__init__(parent)
        self._on_radio_button = None
        self._off_radio_button = None
        self._save_button = None

        self.vbox = QVBoxLayout()
        self.radio_box = QHBoxLayout()

        self.setWidgetPosition()

    def __call__(self, mode):
        self.term_count, self.worker_per_term, self.assistant_mode \
            = self.db.config_repository.get_config()

        self.save_button = '저장하기'

        # TODO: config constraints를 동적으로 가져오도록 수정
        if mode == 'worker':
            val = self.worker_per_term

            self.worker = {
                '1_worker': QRadioButton('1명'),
                '2_worker': QRadioButton('2명'),
                '3_worker': QRadioButton('3명')
            }
            for k, v in self.worker.items():
                self.radio_box.addWidget(v)
                if int(k.split('_')[0]) == val:
                    v.setChecked(True)

            self._save_button.clicked.connect(self.save_worker_config_value_in_db)

        elif mode == 'work_shift':
            val = self.term_count

            self.work_shift = {
                '1_work_shift': QRadioButton('1교대'),
                '2_work_shift': QRadioButton('2교대'),
                '3_work_shift': QRadioButton('3교대'),
                '4_work_shift': QRadioButton('4교대'),
                '12_work_shift': QRadioButton('12교대')
            }
            for k, v in self.work_shift.items():
                self.radio_box.addWidget(v)
                if int(k.split('_')[0]) == val:
                    v.setChecked(True)

            self._save_button.clicked.connect(self.save_work_shift_config_value_in_db)

        else:
            val = self.assistant_mode

            self.on_radio_button, self.off_radio_button = '설정', '해제'
            self._on_radio_button.setChecked(True) if val else self._off_radio_button.setChecked(True)

            self.radio_box.addWidget(self.on_radio_button)
            self.radio_box.addWidget(self.off_radio_button)

            self._save_button.clicked.connect(self.save_radio_checked_value_in_db)

        self.vbox.addStretch(1)
        self.vbox.addLayout(self.radio_box)
        self.vbox.addWidget(self.save_button)
        self.vbox.addStretch(1)

        self.vbox.setAlignment(Qt.AlignCenter)

        self.setLayout(self.vbox)

        self.show()

    @property
    def on_radio_button(self):
        return self._on_radio_button

    @on_radio_button.setter
    def on_radio_button(self, message):
        self._on_radio_button = QRadioButton(message, self)

    @property
    def off_radio_button(self):
        return self._off_radio_button

    @off_radio_button.setter
    def off_radio_button(self, message):
        self._off_radio_button = QRadioButton(message, self)

    @property
    def save_button(self):
        return self._save_button

    @save_button.setter
    def save_button(self, value):
        self._save_button = QPushButton(value)

    def setWidgetPosition(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width() / 2), center.y() - int(self.height() / 2), self.width(), self.height())

    def save_worker_config_value_in_db(self):
        value = [k for k, v in self.worker.items() if v.isChecked()][0]
        if value:
            self.db.config_repository.set_config_worker_per_term(worker_per_term=int(value.split('_')[0]))
        self.close_widget()

    def save_work_shift_config_value_in_db(self):
        value = [k for k, v in self.work_shift.items() if v.isChecked()][0]
        if value:
            term_count = int(value.split('_')[0])
            self.db.config_repository.set_config_term_count(term_count=term_count)
            self.db.work_mode_repository.drop_term_count_related_columns(term_count=term_count)
        self.close_widget()

    def save_radio_checked_value_in_db(self):
        if self._on_radio_button.isChecked() and self._off_radio_button.isChecked() is False:
            self.db.config_repository.set_config_assistant_mode(True)
        elif self._off_radio_button.isChecked() and self._on_radio_button.isChecked() is False:
            self.db.config_repository.set_config_assistant_mode(False)
        else:
            raise ValueError('invalid radio input')
        self.close_widget()

    def close_widget(self):
        self.window().close()

    @classmethod
    def init_widget(cls, mode):
        widget = cls()
        widget(mode)

        return widget


class FileWidget(QWidget):
    mode = None

    label_for_display = {
        "rank": "계급",
        "name": "이름",
        "status": "사수/부사수",
        "weekday_work_count": "평일 카운트",
        "holiday_work_count": "주말 카운트",
    }
    label_for_db = {v: k for k, v in label_for_display.items()}

    day_keys = {
        "평일": "weekday",
        "휴일": "holiday"
    }

    db = database

    def __init__(self, parent=None):
        super(FileWidget, self).__init__(parent)

        self.new_file = False

        self.vbox = QVBoxLayout()
        self.layout = QGridLayout()

        self._file_open = None
        self._add_item = None
        self._add_file = None
        self._edit = None
        self._delete_item = None
        self._delete_all = None
        self._save = None
        self._revert = None

        self.setupButtons()

        self._table = None
        self._row, self._col, self._data = None, None, None

        self.init_table = None
        self.init_row, self.init_col, self.init_data = 0, 0, None

        self.setWidgetPosition()

    def __call__(self, mode):
        self.mode = mode
        self.term_count = self.db.config_repository.get_config()[0]

        self.data = self.db.work_mode_repository.get_all_users_work_mode_columns(term_count=self.term_count)
        self.row, self.col = len(self.data), 1 + 6 + (2 * self.term_count)

        self.table = (self.row, self.col, self.data)
        self.layout.addWidget(self.table, 0, 0, 2, 12)

        # 초기 테이블 정보 저장 (revert시 사용)
        self.init_table = self.table
        self.init_row, self.init_col, self.init_data = self.row, self.col, self.data

        if self.mode == "register":
            self.layout.addWidget(self.file_open, 3, 0, 1, 12)
        elif self.mode == "add":
            self.layout.addWidget(self.add_item, 3, 0, 1, 6)
            self.layout.addWidget(self.add_file, 3, 6, 1, 6)
        elif self.mode == "edit":
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.layout.addWidget(self.edit, 3, 0, 1, 12)
        else:
            self.layout.addWidget(self.delete_item, 3, 0, 1, 6)
            self.layout.addWidget(self.delete_all, 3, 6, 1, 6)

        vbox = QVBoxLayout()
        vbox.addLayout(self.layout)

        self.setLayout(vbox)

    @property
    def vbox(self):
        return self._vbox

    @vbox.setter
    def vbox(self, value):
        self._vbox = value

    @property
    def file_open(self):
        return self._file_open

    @file_open.setter
    def file_open(self, value):
        self._file_open = QPushButton(value)

    @property
    def save(self):
        return self._save

    @save.setter
    def save(self, value):
        self._save = QPushButton(value)

    @property
    def add_item(self):
        return self._add_item

    @add_item.setter
    def add_item(self, value):
        self._add_item = QPushButton(value)

    @property
    def add_file(self):
        return self._add_file

    @add_file.setter
    def add_file(self, value):
        self._add_file = QPushButton(value)

    @property
    def edit(self):
        return self._edit

    @edit.setter
    def edit(self, value):
        self._edit = QPushButton(value)

    @property
    def delete_all(self):
        return self._delete_all

    @delete_all.setter
    def delete_all(self, value):
        self._delete_all = QPushButton(value)

    @property
    def delete_item(self):
        return self._delete_item

    @delete_item.setter
    def delete_item(self, value):
        self._delete_item = QPushButton(value)

    @property
    def revert(self):
        return self._revert

    @revert.setter
    def revert(self, value):
        self._revert = QPushButton(value)

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, value):
        row, col, data = value
        self._table = QTableWidget()
        self._table.setRowCount(row)
        self._table.setColumnCount(col)

        headers = list(self.label_for_db.keys())
        headers.append("근무자")
        for i in range(1, self.term_count + 1):
            headers.append(f"평일 {i}텀")
        for i in range(1, self.term_count + 1):
            headers.append(f"휴일 {i}텀")

        if self.new_file is False:
            headers.insert(0, 'id')

        self._table.setHorizontalHeaderLabels(headers)
        self._table.verticalHeader().setDefaultSectionSize(25)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        enable_flag = True if self.new_file or self.mode == "edit" else False
        j_start = len(self.label_for_display) if self.new_file else len(self.label_for_display) + 1
        for i in range(row):
            for j in range(j_start, col):
                default_val = True
                if self.new_file is not True:
                    if headers[j] == "근무자":
                        default_val = True if data[i]["work_mode"] == "on" else False
                    elif headers[j].startswith("평일") or headers[j].startswith("휴일"):
                        default_val = True if data[i][f'{self.day_keys[headers[j][:2]]}_{headers[j][-2]}'] else False

                cell_widget = self.create_switch_cell_qwidget(
                    track_r=6,
                    thumb_r=9,
                    default_val=default_val,
                    enable_flag=enable_flag
                )
                self._table.setCellWidget(i, j, cell_widget)

        for i, _row in enumerate(data):
            for j, (key, val) in enumerate(_row.items()):
                if key in self.label_for_display.keys() or key in self.label_for_display.values():
                    self._table.setItem(i, j, QTableWidgetItem(str(val)))

        if self.new_file is False:
            self._table.hideColumn(0)

        self._table.resizeRowsToContents()
        self._table.resizeColumnsToContents()

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        self._col = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @staticmethod
    def create_switch_cell_qwidget(track_r, thumb_r, default_val, enable_flag) -> QWidget:
        switch = OnOffSwitch(
            track_radius=track_r,
            thumb_radius=thumb_r,
            default_value=default_val,
            enable_flag=enable_flag
        )

        cell_widget = QWidget()
        layout_cb = QHBoxLayout(cell_widget)
        layout_cb.addWidget(switch)
        layout_cb.setAlignment(Qt.AlignCenter)
        layout_cb.setContentsMargins(0, 0, 0, 0)
        cell_widget.setLayout(layout_cb)

        return cell_widget

    def setWidgetPosition(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width() / 2), center.y() - int(self.height() / 2), self.width(), self.height())

    def setupButtons(self):
        # 인원 등록 메뉴 버튼 (file_open)
        self.setup_file_open_button()

        # 인원 추가 메뉴 버튼 (add_item, add_file)
        self.setup_add_item_button()
        self.setup_add_file_button()

        # 인원 수정 메뉴 버튼 (edit)
        self.setup_edit_button()

        # 인원 삭제 메뉴 버튼 (delete_item, delete_all)
        self.delete_all_button()
        self.delete_item_button()

        # 저장 버튼 (save)
        self.setup_save_button()

        # 되돌리기 버튼 (revert)
        self.setup_revert_button()

    def setup_file_open_button(self):
        if self.file_open:
            self.file_open.deleteLater()
        self.file_open = '등록하기'  # (.csv *.xls *.xml *.xlsx *.xlsm)
        self.file_open.clicked.connect(self.get_csv_file)

    def setup_add_item_button(self):
        if self.add_item:
            self.add_item.deleteLater()

        self.add_item = '입력하여 추가하기'
        self.add_item.clicked.connect(self.add_row)

    def setup_add_file_button(self):
        if self.add_file:
            self.add_file.deleteLater()
        self.add_file = '파일 등록하여 추가하기'
        self.add_file.clicked.connect(self.get_csv_file)

    def setup_edit_button(self):
        if self.edit:
            self.edit.deleteLater()
        self.edit = '수정하기'
        self.edit.clicked.connect(self.edit_db)

    def delete_item_button(self):
        if self.delete_item:
            self.delete_item.deleteLater()
        self.delete_item = '삭제하기'
        self.delete_item.clicked.connect(self.delete_row)

    def delete_all_button(self):
        if self.delete_all:
            self.delete_all.deleteLater()
        self.delete_all = '비우기'
        self.delete_all.clicked.connect(self.clear_db)

    def setup_revert_button(self):
        if self.revert:
            self.revert.deleteLater()
        self.revert = '되돌리기'
        self.revert.clicked.connect(self.revert_table)

    def setup_save_button(self):
        if self.save:
            self.save.deleteLater()
        self.save = '저장하기'
        self.save.clicked.connect(self.save_db)

    def reset_register_mode_button_layout(self):
        self.layout.addWidget(self.table, 0, 0, 2, 12)
        self.layout.addWidget(self.file_open, 3, 0, 1, 4)
        self.layout.addWidget(self.revert, 3, 4, 1, 4)
        self.layout.addWidget(self.save, 3, 8, 1, 4)

    def reset_add_mode_button_layout(self):
        self.layout.addWidget(self.add_item, 3, 0, 1, 3)
        self.layout.addWidget(self.add_file, 3, 3, 1, 3)
        self.layout.addWidget(self.revert, 3, 6, 1, 3)
        self.layout.addWidget(self.save, 3, 9, 1, 3)

    def reset_whole_button_layout(self):
        self.setup_revert_button()
        self.setup_save_button()
        if self.mode == "register":
            self.layout.addWidget(self.file_open, 3, 0, 1, 12)
        elif self.mode == "add":
            self.layout.addWidget(self.add_item, 3, 0, 1, 6)
            self.layout.addWidget(self.add_file, 3, 6, 1, 6)

    def get_csv_file(self):
        file_filter = ['.csv', '.xls', '.xml', '.xlsx', '.xlsm']

        if self.mode == "register" and len(self.data) > 0:
            message_box = setInformationMessageBox(
                self,
                "파일 등록하기",
                "이미 등록된 데이터가 있습니다. 새로 등록하시겠습니까?\n (기존의 데이터가 모두 사라집니다)"
            )
            if message_box is False:
                return

        try:
            dialog = QFileDialog()
            file_dialog = dialog.getOpenFileName(
                self,
                'File Open',
                'c:\\',
                f'Data Files (*{" *".join(file_filter)})'
            )
            file_path = file_dialog[0] or ''

            path = pathlib.Path(file_path)
            parent, name, ext = path.parent, path.name, path.suffix
        except ValueError:
            return setCriticalMessageBox(self, "잘못된 파일 경로입니다.")
        else:
            if not file_path:
                return
            if ext and ext not in file_filter:
                return setCriticalMessageBox(self, f'유효하지 않은 파일 확장자입니다. \n (*{" *".join(file_filter)})"')

        data = []
        if ext == '.csv':
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    data.append(r)
            row, col = len(data), len(data[0])

        else:
            reader = pd.read_excel(file_path, engine='openpyxl')
            keys = list(reader.keys())
            for r in reader.values:
                data.append({keys[i]: v for i, v in enumerate(r)})
            row, col = reader.shape

        self.data = data
        self.row, self.col = len(self.data), 6 + (2 * self.term_count)

        self.new_file = True

        update_table = {
            "register": lambda: self.reset_rows_from_new_csv(),
            "add": lambda: self.add_rows_from_new_csv()
        }
        update_table[self.mode]()

        self.new_file = False
        return

    def get_table_cur_data(self):
        """
        csv 파일에서 읽어온, 아직 db에 저장되지 않은 데이터로,
        user_data에 id값이 포함되어 있지 않음
        """
        user_list = []
        for i in range(self.row):
            user_data, work_mode_option = {}, {}
            for j in range(self.col):
                header = self.table.horizontalHeaderItem(j).text()
                if header == "id":
                    continue

                if header in self.label_for_display.values():
                    user_data[self.label_for_db[header]] = self.table.item(i, j).text()
                else:
                    switch = self.table.cellWidget(i, j).layout().itemAt(0).widget()
                    if header == "근무자":
                        pre_header = "work_mode"
                        value = "on" if switch.isChecked() else "off"
                    elif header[:2] in self.day_keys.keys():
                        day, idx = header.split(" ")
                        pre_header = self.day_keys[day] + "_" + idx[0]
                        value = 1 if switch.isChecked() else 0
                    else:
                        continue
                    work_mode_option[pre_header] = value

            user_list.append({
                "data": user_data,
                "work_mode_option": work_mode_option
            })
        return user_list

    def get_table_raw_data(self):
        """
        db에서 읽어온 table의 raw data로
        user_data값에 해당 user 객체의 id값이 포함
        """
        user_list = []
        for i, _row in enumerate(self.data):
            user_data, work_mode_option = {}, {}
            for j, (key, val) in enumerate(_row.items()):
                if key in self.label_for_display.keys():
                    user_data[key] = val
                else:
                    work_mode_option[key] = val
            user_list.append({
                "data": user_data,
                "work_mode_option": work_mode_option
            })
        return user_list

    def save_db(self):
        message_box = setQuestionMessageBox(self, "저장하시겠습니까?")
        if message_box is False:
            return

        if self.mode == "register":
            self.db.user_repository.delete_all_users()

        self.create_users_from_table_data()

        self.close_widget()

    def create_users_from_table_data(self):
        user_list = self.get_table_cur_data()

        s_row = self.init_row if self.mode == "add" else 0
        for i, user in enumerate(user_list):
            if i < s_row:  # 이미 db에 저장되어 있는 user row는 pass
                continue
            new_user_id = self.db.user_repository.insert_new_user(data=user["data"])
            self.db.work_mode_repository.insert_user_work_mode(
                user_id=new_user_id,
                option=user["work_mode_option"]
            )

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for j in range(len(self.label_for_display) + 1, self.col):
            cell_widget = self.create_switch_cell_qwidget(track_r=6, thumb_r=9, default_val=True, enable_flag=True)
            self.table.setCellWidget(row, j, cell_widget)

        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)

        for i in range(0, self.row):
            for j in range(1, len(self.label_for_display) + 1):
                item = self.table.item(i, j)
                if item:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.reset_add_mode_button_layout()

    def add_rows_from_new_csv(self):
        s = self.table.rowCount()
        for i in range(s, s + self.row):
            self.table.insertRow(i)
            for j in range(len(self.label_for_display) + 1, self.col):
                cell_widget = self.create_switch_cell_qwidget(track_r=6, thumb_r=9, default_val=True, enable_flag=True)
                self.table.setCellWidget(i, j, cell_widget)

        for i in range(s, s + self.row):
            j = 1
            for key, val in self.data[i - s].items():
                if key in self.label_for_display.keys() or key in self.label_for_display.values():
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
                    j += 1

        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        for i in range(0, s):
            for j in range(1, len(self.label_for_display) + 1):
                item = self.table.item(i, j)
                if item:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.table.verticalHeader().setDefaultSectionSize(25)

        self.reset_add_mode_button_layout()

    def reset_rows_from_new_csv(self):
        self.table.setRowCount(0)
        self.table = (self.row, self.col, self.data)
        self.table.verticalHeader().setDefaultSectionSize(25)

        self.reset_register_mode_button_layout()

    def revert_table(self):
        if self.init_table is None:
            return setAboutMessageBox(self, "되돌릴 수 있는 데이터가 없습니다.")

        message_box = setQuestionMessageBox(self, "되돌리시겠습니까?")
        if message_box is False:
            return

        prev_table = self.table
        self.table = (self.init_row, self.init_col, self.init_data)
        self.layout.replaceWidget(prev_table, self.table)
        self.table.verticalHeader().setDefaultSectionSize(25)

        self.reset_whole_button_layout()

    def edit_db(self):
        message_box = setQuestionMessageBox(self, "수정하시겠습니까?")
        if message_box is False:
            return

        _user_list = self.get_table_raw_data()  # 수정되기 전의 data
        new_user_list = self.get_table_cur_data()  # 현재 table에 저장되어 있는 data

        for i, user in enumerate(self.data):
            user_id = user['id']
            if self.db.user_repository.get_user_by_id(user_id=user_id):
                self.db.user_repository.update_user(
                    user_id=user_id,
                    user_data=new_user_list[i]["data"]
                )
                self.db.work_mode_repository.update_user_work_mode(
                    user_id=user_id,
                    option=new_user_list[i]["work_mode_option"]
                )
        self.close_widget()

    def delete_row(self):
        message_box = setQuestionMessageBox(self, "데이터를 삭제하시겠습니까?")
        if message_box is False:
            return

        idx = self.table.selectedRanges()[0]
        s, e = idx.topRow(), idx.bottomRow()

        for i in range(s, e + 1):
            self.db.user_repository.delete_user(user_id=self.data[i]['id'])
        for i in range(e, s - 1, -1):
            x = self.data.pop(i)
            if x:
                self.table.removeRow(i)

    def clear_db(self):
        message_box = setQuestionMessageBox(self, "전부 삭제하시겠습니까?")
        if message_box is False:
            return

        self.db.user_repository.delete_all_users()

        users_cnt = len(self.data)
        for i in range(users_cnt):
            self.table.removeRow(i)

    def close_widget(self):
        self.window().close()

    @classmethod
    def init_db_widget(cls, mode):
        widget = cls()
        widget(mode)

        return widget


class OptionWidget(QWidget):
    db = database

    tree_widget_header_dict = {
        "outside": ["id", "이름", "출발일", "복귀일"],
        "exception": ["id", "이름", "일자", "시작시간", "종료시간"],
        "special_relation": ["id1", "사용자1", "id2", "사용자2"]
    }

    def __init__(self, parent=None):
        super(OptionWidget, self).__init__(parent)

        self.listbox_data = self.db.user_repository.get_all_users()

        self.search_content = QLineEdit()
        self._search_button = None
        self._add_button = None
        self._remove_button = None
        self._save_button = None

    def setupLayout(self):
        search = QHBoxLayout()
        search.addWidget(self.search_content)
        search.addWidget(self.search_button)

        listbox = QHBoxLayout()
        listbox.addWidget(self.user_listbox)

        buttons = QVBoxLayout()
        buttons.addStretch(1)
        if self.mode != "special_relation":
            buttons.addWidget(self.add_button)
        buttons.addWidget(self.remove_button)
        buttons.addWidget(self.save_button)
        buttons.addStretch(1)

        selected = QHBoxLayout()
        selected.addWidget(self.selected_box)

        layout = QGridLayout()
        layout.addLayout(search, 0, 0, 1, 4)
        layout.addLayout(listbox, 1, 0)
        layout.addLayout(buttons, 1, 1)
        layout.addLayout(selected, 1, 2)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 4)
        lr_margin, tb_margin = self.width() * 0.05, self.height() * 0.05
        layout.setContentsMargins(lr_margin, tb_margin, lr_margin, tb_margin)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setupButtons(self):
        self.setup_search_button()
        self.setup_add_button()
        self.setup_remove_button()
        self.setup_save_button()

    def setup_search_button(self):
        if self.search_button:
            self.search_button.deleteLater()
        self.search_button = "검색"
        self.search_button.clicked.connect(self.display_users_name_in_listbox)

    def setup_add_button(self):
        if self.add_button:
            self.add_button.deleteLater()
        self.add_button = "추가"
        self.add_button.clicked.connect(self.add_item_to_select_box)

    def setup_remove_button(self):
        if self.remove_button:
            self.remove_button.deleteLater()
        self.remove_button = "삭제"
        self.remove_button.clicked.connect(self.remove_item_from_select_box)

    def setup_save_button(self):
        if self.save_button:
            self.save_button.deleteLater()
        self.save_button = "저장"
        if self.mode == "special_relation":
            self.save_button.clicked.connect(self.save_relation_to_db)
        else:
            self.save_button.clicked.connect(self.save_exp_datetime_to_db)

    @property
    def search_button(self):
        return self._search_button

    @search_button.setter
    def search_button(self, value):
        self._search_button = QPushButton(value)

    @property
    def save_button(self):
        return self._save_button

    @save_button.setter
    def save_button(self, value):
        self._save_button = QPushButton(value)

    @property
    def add_button(self):
        return self._add_button

    @add_button.setter
    def add_button(self, value):
        self._add_button = QPushButton(value)
        self._add_button.setStyleSheet("")

    @property
    def remove_button(self):
        return self._remove_button

    @remove_button.setter
    def remove_button(self, value):
        self._remove_button = QPushButton(value)
        self._remove_button.setStyleSheet("")

    def __call__(self, mode):
        self.mode = mode
        self.term_count = self.db.config_repository.get_config()[0]

        header_labels = self.tree_widget_header_dict[mode]

        if mode == 'special_relation':
            admin = AdminDialog(login_user=settings.login_user)
            admin.exec_()
            if admin.access_approval is False:
                return False

            exp_data = self.db.user_repository.get_all_exp_relation()
        else:
            exp_data = self.db.work_mode_repository.get_exp_datetime_exists_users()

        self.selected_box = DropTreeWidget.tree_widget(mode, exp_data, header_labels)

        self.user_listbox = DragTreeWidget.list_widget(["아이디", "이름"])
        self.display_users_name_in_listbox()

        if mode == 'special_relation':
            self.user_listbox.setDragMode(mode)
            self.selected_box.setDropMode()

        self.setupButtons()
        self.setupLayout()

        return True

    def display_users_name_in_listbox(self):
        q = self.search_content.text()
        if q == '':
            self.listbox_data = self.db.user_repository.get_all_users()
        else:
            self.listbox_data = self.db.user_repository.get_user_by_name(name=q)

        self.user_listbox.clear()

        if self.listbox_data is None:
            print('검색 결과가 없습니다.')
            return

        items = []
        if self.mode == 'special_relation':
            for d in self.listbox_data:
                user_id, name = d["id"], d["name"]
                i = QTreeWidgetItem()
                i.setText(0, str(user_id))
                i.setText(1, name)
                i.setTextAlignment(1, Qt.AlignHCenter)
                items.append(i)
        else:
            selected_names = []
            for i in range(self.selected_box.topLevelItemCount()):
                selected_names.append(self.selected_box.topLevelItem(i).text(1))

            for d in self.listbox_data:
                user_id, name = d["id"], d["name"]
                if name not in selected_names:
                    i = QTreeWidgetItem()
                    i.setText(0, str(user_id))
                    i.setText(1, name)
                    i.setTextAlignment(1, Qt.AlignHCenter)
                    items.append(i)

        self.user_listbox.addTopLevelItems(items)
        return

    def add_item_to_select_box(self):
        items = self.user_listbox.selectedItems()
        if len(items) == 0:
            return

        item = items[0]
        user_id, name = item.text(0), item.text(1)

        row = self.user_listbox.currentIndex().row()
        removed_from_userbox = self.user_listbox.takeTopLevelItem(row)

        tree_widget_item = QTreeWidgetItem()
        tree_widget_item.setText(0, user_id)
        tree_widget_item.setText(1, name)
        tree_widget_item.setTextAlignment(1, Qt.AlignCenter)

        self.selected_box.addTopLevelItem(tree_widget_item)

        departure = DateEdit.set_date_edit_widget(QDate.currentDate(), "yyyy/MM/dd")
        if self.mode == 'outside':
            arrival = DateEdit().set_date_edit_widget(QDate.currentDate().addDays(7), "yyyy/MM/dd")

            departure.dateChanged.connect(lambda: departure.reset_start_date(arrival))
            arrival.dateChanged.connect(lambda: arrival.reset_end_date(departure))

            self.selected_box.setItemWidget(tree_widget_item, 2, departure)
            self.selected_box.setItemWidget(tree_widget_item, 3, arrival)
        elif self.mode == 'exception':
            start_time = TimeEdit.set_time_edit_widget(QTime().currentTime(), "hh:mm")
            end_time = TimeEdit.set_time_edit_widget(QTime.currentTime().addSecs(60 * 60 * (24 / self.term_count)), "hh:mm")

            start_time.timeChanged.connect(lambda: start_time.reset_start_time(end_time))
            end_time.timeChanged.connect(lambda: end_time.reset_end_time(start_time))

            self.selected_box.setItemWidget(tree_widget_item, 2, departure)
            self.selected_box.setItemWidget(tree_widget_item, 3, start_time)
            self.selected_box.setItemWidget(tree_widget_item, 4, end_time)

    def remove_item_from_select_box(self):
        row = self.selected_box.currentIndex().row()
        removed_item = self.selected_box.takeTopLevelItem(row)
        if not removed_item:
            return

        if self.mode != "special_relation":
            name = removed_item.text(0)
            # BUGFIX: addItem()
            # self.user_listbox.addItem(name)

    def get_drop_widget_data(self):
        cnt = self.selected_box.columnCount()

        _data = []
        for i in range(self.selected_box.topLevelItemCount()):
            item = self.selected_box.topLevelItem(i)

            row_data = {}
            for j in range(cnt):
                item_widget = self.selected_box.itemWidget(item, j)
                row_data[self.tree_widget_header_dict[self.mode][j]] = item_widget.text() if item_widget else item.text(j)
            _data.append(row_data)

        return _data

    def save_exp_datetime_to_db(self):
        _data = self.get_drop_widget_data()
        if _data is None:
            print('저장할 데이터가 없습니다')
            return

        message_box = setQuestionMessageBox(self, "저장하시겠습니까?")
        if message_box is False:
            return

        # TODO: exp_datetime 수정시, workmode 수정
        if self.mode == "outside":
            for d in _data:
                if d["출발일"] > d["복귀일"]:
                    print("잘못된 날짜 설정 옵션입니다. 저장할 수 없습니다.")
                    continue

                self.db.work_mode_repository.update_exp_datetime(
                    user_id=d["id"],
                    start=d["출발일"] + " " + "00:00",
                    end=d["복귀일"] + " " + "23:59"
                )
        elif self.mode == "exception":
            for d in _data:
                if d["시작시간"] > d["종료시간"]:
                    print("잘못된 시간 설정 옵션입니다. 저장할 수 없습니다.")
                    continue

                self.db.work_mode_repository.update_exp_datetime(
                    user_id=d["id"],
                    start=d["일자"] + " " + d["시작시간"],
                    end=d["일자"] + " " + d["종료시간"]
                )

        self.close_widget()

    def save_relation_to_db(self):
        _data = self.get_drop_widget_data()
        if _data is None:
            print('저장할 데이터가 없습니다')
            return

        message_box = setQuestionMessageBox(self, "저장하시겠습니까?")
        if message_box is False:
            return

        for d in _data:
            self.db.user_repository.insert_exp_relation(
                user_1_id=int(d["id1"]),
                user_1_name=d["사용자1"],
                user_2_id=int(d["id2"]),
                user_2_name=d["사용자2"]
            )

        self.close_widget()

    def close_widget(self):
        self.window().close()

    @classmethod
    def init_option_widget(cls, mode):
        widget = cls()

        success = widget(mode)
        return widget if success else None


class DragTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(DragTreeWidget, self).__init__(parent)

    def __call__(self, header_labels):
        self.setTreeWidgetHeader(header_labels)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def dragEnterEvent(self, event):
        event.accept()

    def setDragMode(self, menu):
        self.setDragDropMode(QAbstractItemView.DragOnly)

        if menu == "special_relation":
            self.setDefaultDropAction(Qt.CopyAction)
        else:
            self.setDefaultDropAction(Qt.MoveAction)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def setTreeWidgetHeader(self, labels):
        self.setHeaderLabels(labels)
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.hideColumn(0)

    @classmethod
    def list_widget(cls, header_labels):
        widget = cls()
        widget(header_labels)
        return widget


class DropTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(DropTreeWidget, self).__init__(parent)

    def __call__(self, mode, data, header_labels):
        self.mode = mode
        self.raw_data = data
        self.added_data = None

        self.setTreeWidgetHeader(header_labels)
        self.initTreeWidgetItems()

    def init_special_relation_tree(self):
        for v in self.raw_data:
            item = QTreeWidgetItem()
            item.setText(0, str(v["user_1_id"]))
            item.setText(1, v["user_1_name"])
            item.setText(2, str(v["user_2_id"]))
            item.setText(3, v["user_2_name"])
            item.setTextAlignment(1, Qt.AlignHCenter)
            item.setTextAlignment(3, Qt.AlignHCenter)
            self.addTopLevelItem(item)

        return True

    def init_outside_relation_tree(self):
        for v in self.raw_data:
            item = QTreeWidgetItem()
            item.setText(0, str(v["user_id"]))
            item.setText(1, v["name"])
            item.setTextAlignment(1, Qt.AlignHCenter)

            today = QDate.currentDate()

            date_start = QDate.fromString(v["exp_start_datetime"].split(' ')[0], "yyyy/MM/dd")
            date_end = QDate.fromString(v["exp_end_datetime"].split(' ')[0], "yyyy/MM/dd")

            if today <= date_start:
                widget_s_date, widget_e_date = date_start, date_end
            elif date_start < today < date_end:
                widget_s_date, widget_e_date = today, date_end
            elif today == date_end:
                widget_s_date, widget_e_date = today, today
            else:
                continue

            start_date = DateEdit.set_date_edit_widget(date=widget_s_date, date_format="yyyy/MM/dd")
            end_date = DateEdit.set_date_edit_widget(date=widget_e_date, date_format="yyyy/MM/dd")

            start_date.dateChanged.connect(lambda: start_date.reset_start_date(start_date))
            end_date.dateChanged.connect(lambda: end_date.reset_end_date(end_date))

            self.addTopLevelItem(item)
            self.setItemWidget(item, 2, start_date)
            self.setItemWidget(item, 3, end_date)

        return True

    def init_exception_relation_tree(self):
        for v in self.raw_data:
            item = QTreeWidgetItem()
            item.setText(0, str(v["user_id"]))
            item.setText(1, v["name"])
            item.setTextAlignment(1, Qt.AlignHCenter)

            today = QDate.currentDate()

            exp_start_dt = v["exp_start_datetime"].split(' ')
            date_start = QDate.fromString(exp_start_dt[0], "yyyy/MM/dd")
            time_start = QTime.fromString(exp_start_dt[1], "hh:mm")

            exp_end_dt = v["exp_end_datetime"].split(' ')
            date_end = QDate.fromString(exp_end_dt[0], "yyyy/MM/dd")
            time_end = QTime.fromString(exp_end_dt[1], "hh:mm")

            if today <= date_start:
                widget_date = date_start
                widget_s_time, widget_e_time = time_start, QTime(23, 59, 59)
            elif date_start < today < date_end:
                widget_date = today
                widget_s_time, widget_e_time = QTime(0, 00, 00), QTime(23, 59, 59)
            elif today == date_end:
                widget_date = date_end
                widget_s_time, widget_e_time = QTime(0, 00, 00), time_end
            else:
                continue

            date = DateEdit.set_date_edit_widget(date=widget_date, date_format="yyyy/MM/dd")
            start_time = TimeEdit.set_time_edit_widget(time=widget_s_time, time_format="hh:mm")
            end_time = TimeEdit.set_time_edit_widget(time=widget_e_time, time_format="hh:mm")

            start_time.timeChanged.connect(lambda: start_time.reset_start_time(start_time))
            end_time.timeChanged.connect(lambda: end_time.reset_start_time(end_time))

            self.addTopLevelItem(item)
            self.setItemWidget(item, 2, date)
            self.setItemWidget(item, 3, start_time)
            self.setItemWidget(item, 4, end_time)

        return True

    def setDropMode(self):
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)
        self.setDragEnabled(False)

    def dropEvent(self, event):
        idx = self.indexAt(event.pos())
        row, col = idx.row(), idx.column()

        selected = event.source().selectedItems()[0]
        new_id, new_name = selected.text(0), selected.text(1)
        self.addTreeWidgetItem(row, col, new_id, new_name)
        event.accept()

    def addTreeWidgetItem(self, row, col, id_value, value):
        if row == -1 or col == -1:
            item = QTreeWidgetItem()
            item.setText(0, id_value)
            item.setText(1, value)
            item.setTextAlignment(1, Qt.AlignHCenter)
            self.addTopLevelItem(item)
        elif col == 3:
            item = self.topLevelItem(row)
            if item:
                item.setText(2, id_value)
                item.setText(3, value)
                item.setTextAlignment(3, Qt.AlignHCenter)

    def initTreeWidgetItems(self):
        if self.mode == "special_relation":
            self.init_special_relation_tree()

        elif self.mode == "outside":
            self.init_outside_relation_tree()

        elif self.mode == "exception":
            self.init_exception_relation_tree()

    def setTreeWidgetHeader(self, labels):
        self.setHeaderLabels(labels)
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setColumnHidden(0, True)

        if self.mode == "special_relation":
            self.setColumnHidden(2, True)
            self.header().resizeSection(1, 50)
            self.header().resizeSection(3, 50)

        elif self.mode == "outside":
            self.header().resizeSection(1, 20)
            self.header().resizeSection(2, 40)
            self.header().resizeSection(3, 40)
        elif self.mode == "exception":
            self.header().resizeSection(1, 20)
            self.header().resizeSection(2, 40)
            self.header().resizeSection(3, 20)
            self.header().resizeSection(4, 20)

    @classmethod
    def tree_widget(cls, mode, data, header_labels):
        widget = cls()
        widget(mode, data, header_labels)
        return widget


class OnOffSwitch(QCheckBox):
    def __init__(
            self,
            parent=None,
            track_radius=None,
            thumb_radius=None,
            default_value=None,
            enable_flag=None
    ):
        super().__init__(parent=parent)

        self._track_radius = track_radius
        self._thumb_radius = thumb_radius

        self._margin = max(0, (self._thumb_radius - self._track_radius) / 2)
        self._base_offset = max(self._thumb_radius, self._track_radius)

        self._end_offset = {
            True: self._base_offset + 7,
            False: self._base_offset
        }
        self._offset = self._base_offset

        self.setCheckable(True)
        self.setFixedSize(18 + self._base_offset * 2, 18)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setChecked(default_value)
        self.setEnabled(enable_flag)

        palette = self.palette()
        self._track_color = {True: palette.highlight(), False: palette.dark()}
        self._thumb_color = {True: palette.highlight(), False: palette.light()}
        self._track_opacity = 0.5

        self.animation = QPropertyAnimation(self, b"offset", self)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.setDuration(150)

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def hitButton(self, pos):
        return self.contentsRect().contains(pos)

    def sizeHint(self):
        return QSize(4 * self._track_radius + 2 * self._margin, 2 * self._track_radius + 2 * self._margin)

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._end_offset[checked]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.offset = self._end_offset[self.isChecked()]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)

        track_opacity = self._track_opacity
        thumb_opacity = 1.0
        if self.isEnabled():
            track_brush = self._track_color[self.isChecked()]
            thumb_brush = self._thumb_color[self.isChecked()]
        else:
            track_opacity *= 0.8
            track_brush = self.palette().shadow()
            thumb_brush = self.palette().mid()

        p.setBrush(track_brush)
        p.setOpacity(track_opacity)
        p.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin,
            self.height() - 2 * self._margin,
            self._track_radius,
            self._track_radius,
        )

        p.setBrush(thumb_brush)
        p.setOpacity(thumb_opacity)
        if self.isChecked():
            p.drawEllipse(
                self._offset,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            )
        else:
            p.drawEllipse(
                self._offset - self._thumb_radius,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            )

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.animation.setStartValue(self._offset)
            self.animation.setEndValue(self._end_offset[self.isChecked()])
            self.animation.start()

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)


class DateEdit(QDateEdit):
    def __init__(self, parent=None):
        super(DateEdit, self).__init__(parent=parent)

    def __call__(self, date: QDate, date_format: str):
        self.setDate(date)
        self.setDisplayFormat(date_format)
        self.dateChanged.connect(self.set_date_range)

    def resetDate(self, date: QDate):
        self.setDate(date)

    def set_date_range(self):
        if self.date() >= QDate.currentDate():
            return

        message_box = setWarningMessageBox(self, "오늘 일자보다 작게 설정할 수 없습니다.")
        self.resetDate(QDate.currentDate())
        return

    def reset_start_date(self, end_d: QDateEdit):
        start, end = self.date(), end_d.date()
        if start.daysTo(end) >= 0:
            return

        self.resetDate(end.addDays(-1))
        return setWarningMessageBox(self, "도착일을 출발일보다 작게 설정할 수 없습니다.")

    def reset_end_date(self, start_d: QDateEdit):
        start, end = start_d.date(), self.date()
        if start.daysTo(end) >= 0:
            return

        self.resetDate(start.addDays(1))
        return setWarningMessageBox(self, "도착일을 출발일보다 작게 설정할 수 없습니다.")

    @classmethod
    def set_date_edit_widget(cls, date, date_format: str):
        _date = QDate.fromString(date, date_format) if isinstance(date, str) else date
        date_edit = cls()
        date_edit(_date, date_format)

        return date_edit


class TimeEdit(QTimeEdit):
    def __init__(self, parent=None):
        super(TimeEdit, self).__init__(parent)

    def __call__(self, time: QTime, time_format: str):

        self.setTime(time)
        self.setDisplayFormat(time_format)
        self.setTimeRange(QTime(0, 00, 00), QTime(23, 59, 59))

    def reset_start_time(self, end_t: QTimeEdit):
        start, end = self.time(), end_t.time()
        print(start)
        print(end)

    def reset_end_time(self, start_t: QTimeEdit):
        start, end = start_t.time(), self.time()
        pass

    @classmethod
    def set_time_edit_widget(cls, time, time_format: str):
        _time = QTime.fromString(time, time_format) if isinstance(time, str) else time
        time_edit = cls()
        time_edit(_time, time_format)

        return time_edit
