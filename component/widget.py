import csv
import pandas as pd
import pathlib
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
    def __init__(self, parent=None, db=None):
        super(FileWidget, self).__init__(parent)
        self.db = db
        self._vbox = None

        self._file_open = None
        self._file_save = None
        self._table = None

        self._table_data_dict = None

        self.init_widget()
        self.get_file()

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
    def table(self):
        return self._table

    @table.setter
    def table(self, value):
        row, col, data = value
        self._table = QTableWidget()
        self._table.setRowCount(row)
        self._table.setColumnCount(col)
        self._table.setHorizontalHeaderLabels(list(data[0].keys()))

        self.table_data_dict = data
        for i, _row in enumerate(data):
            for j, (key, value) in enumerate(_row.items()):
                self._table.setItem(i, j, QTableWidgetItem(value))

        self._table.resizeRowsToContents()
        self._table.resizeColumnsToContents()

    @property
    def table_data_dict(self):
        return self._table_data_dict

    @table_data_dict.setter
    def table_data_dict(self,value):
        self._table_data_dict = value

    def get_file(self):
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

        prev_table = self.table
        self.table = (row, col, data)
        self.vbox.replaceWidget(prev_table, self.table)

        self.vbox.addWidget(self.table)
        self.vbox.addWidget(self.file_open)
        self.vbox.addWidget(self.file_save)

        self.setLayout(self.vbox)

        # TODO: table 크기에 맞게 widget/window 사이즈 조정
        self.window().resize(self.table.width(), self.table.height())

    def save_file(self):
        # TODO: 수정된 table의 data를 self.table_data_dict에 set한 뒤, DB에 저장
        print(self.table_data_dict)

    def init_widget(self):
        self.vbox = QVBoxLayout()

        self.file_open = '파일 선택하기 (.csv *.xls *.xml *.xlsx *.xlsm)'
        self.file_open.clicked.connect(self.get_file)

        self.file_save = '파일 저장하기'
        self.file_save.clicked.connect(self.save_file)
