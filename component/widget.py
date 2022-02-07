import csv
import pandas as pd
import pathlib

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QRadioButton, QPushButton, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QFileDialog, \
    QTableWidget, QTableWidgetItem, QMessageBox

from db import database
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

        self._label_title = None

        self._on_radio_button = None
        self._off_radio_button = None
        self._save_button = None

        self.vbox = QVBoxLayout()
        self.radio_box = QHBoxLayout()

    def __call__(self, mode):
        self.term_count, self.worker_per_term, self.assistant_mode \
            = self.db.config_repository.get_config()

        self.label_title = self.message_dict[mode]
        self.label_title.setAlignment(Qt.AlignCenter)
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

        self.vbox.addWidget(self.label_title)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.radio_box)
        self.vbox.addWidget(self.save_button)

        self.vbox.setAlignment(Qt.AlignCenter)

        self.setLayout(self.vbox)

        self.setGeometry(300, 300, 200, 200)
        self.show()

    @property
    def label_title(self):
        return self._label_title

    @label_title.setter
    def label_title(self, message):
        self._label_title = QLabel(message)

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

    def save_worker_config_value_in_db(self):
        value = [k for k, v in self.worker.items() if v.isChecked()][0]
        if value:
            self.db.config_repository.set_config_worker_per_term(worker_per_term=int(value.split('_')[0]))
        self.close_widget()

    def save_work_shift_config_value_in_db(self):
        value = [k for k, v in self.work_shift.items() if v.isChecked()][0]
        if value:
            self.db.config_repository.set_config_term_count(term_count=int(value.split('_')[0]))
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
    db = database

    def __init__(self, parent=None):
        super(FileWidget, self).__init__(parent)

        self.vbox = QVBoxLayout()

        self.file_open = '파일 선택하기 (.csv *.xls *.xml *.xlsx *.xlsm)'
        self.file_open.clicked.connect(self.get_csv_file)

        self.file_save = '파일 저장하기'
        self.file_save.clicked.connect(self.save_file)

        self.edit = '데이터베이스 수정하기'
        self.edit.clicked.connect(self.edit_db)

        self.delete_item = '삭제'
        self.delete_item.clicked.connect(self.delete_row)
        self.delete_all = '데이터베이스 비우기'
        self.delete_all.clicked.connect(self.clear_db)

        self._table = None
        self._row, self._col, self._data = None, None, None

    def __call__(self, mode):
        self.mode = mode
        self.term_count = self.db.config_repository.get_config()[0]

        self.label_for_display = {
            "rank": "계급",
            "name": "이름",
            "status": "사수/부사수",
            "weekday_work_count": "평일 카운트",
            "holiday_work_count": "주말 카운트",
            "work_mode": "근무자"
        }
        self.label_for_db = {v: k for k, v in self.label_for_display.items()}

        if mode == 'register':
            self.vbox.addWidget(self.file_open)
            self.vbox.addWidget(self.file_save)
            self.row, self.col, self.data = self.get_csv_file()
        else:
            self.data = self.db.work_mode_repository.get_all_users_work_mode_columns(term_count=self.term_count)
            self.row, self.col = len(self.data), 1 + 6 + (2 * self.term_count)

            if mode == 'edit/view':
                self.vbox.addWidget(self.edit)
            elif mode == 'delete':
                self.vbox.addWidget(self.delete_item)
                self.vbox.addWidget(self.delete_all)

        prev_table = self.table
        self.table = (self.row, self.col, self.data)
        self.reset_widget(prev_table=prev_table)
        self.setLayout(self.vbox)

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
    def file_save(self):
        return self._file_save

    @file_save.setter
    def file_save(self, value):
        self._file_save = QPushButton(value)

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
    def table(self):
        return self._table

    @table.setter
    def table(self, value):
        row, col, data = value
        self._table = QTableWidget()
        self._table.setRowCount(row)
        self._table.setColumnCount(col)
        print(col)

        headers = list(self.label_for_db.keys())
        for i in range(1, self.term_count + 1):
            headers.append(f"평일_{i}")
            headers.append(f"휴일_{i}")
        print(headers)

        if self.mode != 'register':
            headers.insert(0, 'id')
        self._table.setHorizontalHeaderLabels(headers)

        for i, _row in enumerate(data):
            for j, (key, val) in enumerate(_row.items()):
                self._table.setItem(i, j, QTableWidgetItem(str(val)))

        if self.mode != 'register':
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

    def get_csv_file(self):
        dialog = QFileDialog()
        file_filter = ['.csv', '.xls', '.xml', '.xlsx', '.xlsm']

        file_dialog = dialog.getOpenFileName(
            self,
            'File Open',
            'c:\\',
            f'Data Files (*{" *".join(file_filter)})'
        )
        file_path = file_dialog[0] or ''
        try:
            path = pathlib.Path(file_path)
            parent, name, ext = path.parent, path.name, path.suffix
        except ValueError:
            raise ValueError('invalid file path')
        else:
            print(ext)
            if ext not in file_filter:
                raise ValueError(f'invalid file extension (*{" *".join(file_filter)})')

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

        return row, col, data

    def get_table_cur_data(self):
        """
        csv 파일에서 읽어온, 아직 db에 저장되지 않은 데이터로,
        user_data에 id값이 포함되어 있지 않음
        """
        day_keys = {
            "평일": "weekday",
            "휴일": "holiday"
        }
        user_list = []
        for i in range(self.row):
            user_data, work_mode_option = {}, {}
            for j in range(self.col):
                val = self.table.horizontalHeaderItem(j).text()
                if val in self.label_for_display.values():
                    user_data[self.label_for_db[val]] = self.table.item(i, j).text()
                else:
                    if val == "id":
                        _val = val
                    else:
                        day, num = val.split("_")
                        _val = day_keys[day] + "_" + num
                    work_mode_option[_val] = int(self.table.item(i, j).text())
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

    def save_file(self):
        message = QMessageBox.question(self, "QMessageBox", "저장하시겠습니까?", QMessageBox.No | QMessageBox.Yes)
        if message == QMessageBox.Yes:
            user_list = self.get_table_cur_data()

            default_work_mode = {}
            for i in range(self.term_count):
                default_work_mode[f'weekday_{i + 1}'] = 1
                default_work_mode[f'holiday_{i + 1}'] = 1

            for user in user_list:
                new_user_id = self.db.user_repository.insert_new_user(data=user["data"])
                self.db.work_mode_repository.insert_user_work_mode(
                    user_id=new_user_id,
                    option=default_work_mode
                )
            self.close_widget()
        else:
            return

    def edit_db(self):
        message = QMessageBox.question(self, "QMessageBox", "수정하시겠습니까?", QMessageBox.No | QMessageBox.Yes)
        if message == QMessageBox.Yes:
            _user_list = self.get_table_raw_data()      # 수정되기 전의 data
            new_user_list = self.get_table_cur_data()   # 현재 table에 저장되어 있는 data

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
        else:
            return

    def delete_row(self):
        message = QMessageBox.question(self, "QMessageBox", "데이터를 삭제하시겠습니까?", QMessageBox.No | QMessageBox.Yes)
        if message == QMessageBox.Yes:
            idx = self.table.selectedRanges()[0]
            s, e = idx.topRow(), idx.bottomRow()

            for i in range(s, e + 1):
                self.db.user_repository.delete_user(user_id=self.data[i]['id'])

            for i in range(e, s - 1, -1):
                x = self.data.pop(i)
                if x:
                    self.table.hideRow(i)
        else:
            return

    def clear_db(self):
        message = QMessageBox.question(self, "QMessageBox", "전부 삭제하시겠습니까?", QMessageBox.No | QMessageBox.Yes)
        if message == QMessageBox.Yes:
            users_cnt = len(self.data)

            self.db.user_repository.delete_all_users()
            for i in range(users_cnt):
                self.table.hideRow(i)
        else:
            return

    # TODO: table 크기에 맞게 widget/window 사이즈 조정
    def reset_widget(self, prev_table):
        if prev_table:
            self.vbox.replaceWidget(prev_table, self.table)
        else:
            self.vbox.addWidget(self.table)

    def close_widget(self):
        self.window().close()

    @classmethod
    def init_db_widget(cls, mode):
        widget = cls()
        widget(mode)

        return widget


class OptionWidget(QWidget):
    def __init__(self, parent=None):
        super(OptionWidget, self).__init__(parent)

    def __call__(self, mode):
        pass

    @classmethod
    def init_option_widget(cls, mode):
        widget = cls()
        widget(mode)

        return widget
