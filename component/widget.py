import csv
import pandas as pd
import pathlib

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QWidget, QRadioButton, QPushButton, QVBoxLayout, QSpinBox, QLabel, QFileDialog, \
    QTableWidget, QTableWidgetItem, QDesktopWidget


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
        spinbox_value = self._spinbox.value()
        if self.mode == 'worker':
            self.db.config_repository.set_config_worker_per_term(spinbox_value)
        elif self.mode == 'workshift':
            self.db.config_repository.set_config_term_count(spinbox_value)

            self.db.work_mode_repository.drop_work_mode_table()
            self.db.work_mode_repository.create_work_mode_table(term_count=spinbox_value)
        self.close_widget()

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

        # TODO: window 위치 조정하기
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def close_widget(self):
        self.window().close()


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
        if self._on_radio_button.isChecked() and self._off_radio_button.isChecked() is False:
            self.db.config_repository.set_config_assistant_mode(True)
        elif self._off_radio_button.isChecked() and self._on_radio_button.isChecked() is False:
            self.db.config_repository.set_config_assistant_mode(False)
        else:
            raise ValueError('invalid radio input')
        self.close_widget()

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

    def close_widget(self):
        self.window().close()


class FileWidget(QWidget):
    mode = None

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

    def __call__(self, _db, mode):
        self.db = _db
        self.mode = mode
        self.term_count = self.db.config_repository.get_config()[0]

        self.label_for_display = {
            "rank": "계급",
            "name": "이름",
            "status": "사수/부사수",
            "weekday_work_count": "평일 카운트",
            "weekday_work_count": "주말 카운트"
        }
        self.label_for_db = {v: k for k, v in self.label_for_display.items()}

        if mode == 'register':
            self.vbox.addWidget(self.file_open)
            self.vbox.addWidget(self.file_save)
            self.row, self.col, self.data = self.get_csv_file()
        else:
            self.data = self.db.work_mode_repository.get_all_users_work_mode_columns(term_count=self.term_count)
            self.row, self.col = len(self.data), 4 + (2 * self.term_count) + 1

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
        user_list = []
        for i in range(self.row):
            user_data, work_mode_option = {}, {}
            for j in range(self.col):
                val = self.table.horizontalHeaderItem(j).text()
                if val in self.label_for_display.values():
                    user_data[self.label_for_db[val]] = self.table.item(i, j).text()
                else:
                    work_mode_option[val] = self.table.item(i, j).text()
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
        user_list = self.get_table_cur_data()
        print(user_list)
        for user in user_list:
            new_user_id = self.db.user_repository.insert_new_user(data=user["data"])
            self.db.work_mode_repository.insert_user_work_mode(
                user_id=new_user_id,
                option=user["work_mode_option"]
            )

    def edit_db(self):
        # FEATURE: 수정 전/후 데이터 구분하기
        _user_list = self.get_table_raw_data()      # 수정되기 전의 data
        new_user_list = self.get_table_cur_data()   # 현재 table에 저장되어 있는 data
        for i, user in enumerate(_user_list):
            user_id = user["data"]["id"]
            if self.db.user_repository.get_user_by_id(user_id=user_id):
                self.db.user_repository.update_user(
                    user_id=user_id,
                    user_data=new_user_list[i]["data"]
                )
                self.db.work_mode_repository.update_user_work_mode(
                    user_id=user_id,
                    option=user["work_mode_option"]
                )

    def delete_row(self):
        # FEATURE: 유저 row 삭제 구현하기
        idx = self.table.selectionModel().selectedIndexes()
        for i in idx:
            print(i.row())

    def clear_db(self):
        # FEATURE: db 전체 삭제
        pass

    # TODO: table 크기에 맞게 widget/window 사이즈 조정
    def reset_widget(self, prev_table):
        if prev_table:
            self.vbox.replaceWidget(prev_table, self.table)
        else:
            self.vbox.addWidget(self.table)

    @classmethod
    def init_db_register_widget(cls, db):
        widget = cls()
        widget(db, 'register')
        return widget

    @classmethod
    def init_db_edit_widget(cls, db):
        widget = cls()
        widget(db, 'edit/view')
        return widget

    @classmethod
    def init_db_delete_widget(cls, db):
        widget = cls()
        widget(db, 'delete')
        return widget
