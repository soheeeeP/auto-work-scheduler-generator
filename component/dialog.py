import pyrebase
import os
import hashlib
from base64 import b64encode, b64decode

from dotenv import load_dotenv

from PyQt5.QtWidgets import QPushButton, QLineEdit, QGridLayout, QDialog, QLabel, QDesktopWidget, QMessageBox

load_dotenv()

config = {
    "apiKey": os.environ.get("apiKey"),
    "authDomain": os.environ.get("authDomain"),
    "databaseURL": os.environ.get("databaseURL"),
    "projectId": os.environ.get("projectId"),
    "storageBucket": os.environ.get("storageBucket"),
    "messagingSenderId": os.environ.get("messagingSenderId"),
    "appId": os.environ.get("appId")
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def setCriticalMessageBox(window, message):
    box = QMessageBox.critical(window, "QMessageBox", message, QMessageBox.Close)

    center = QDesktopWidget().availableGeometry().center()
    window.setGeometry(center.x() - int(window.width / 2), center.y() - int(window.height / 2), window.width, window.height)
    return box


class LogInDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.login_user_data = None

        self.width = 300
        self.height = 200

        self.id_entry = QLineEdit()
        self.pw_entry = QLineEdit()
        self.pw_entry.setEchoMode(QLineEdit.Password)

        self.sign_in = "로그인"
        self.sign_up = "회원가입"
        self.sign_in.clicked.connect(self.signInClicked)
        self.sign_up.clicked.connect(self.signUpClicked)

        self.setupLayout()

    @property
    def login_user_data(self):
        return self._login_user_data

    @login_user_data.setter
    def login_user_data(self, value):
        self._login_user_data = value

    @property
    def sign_in(self):
        return self._sign_in

    @sign_in.setter
    def sign_in(self, value):
        self._sign_in = QPushButton(value)

    @property
    def sign_up(self):
        return self._sign_up

    @sign_up.setter
    def sign_up(self, value):
        self._sign_up = QPushButton(value)

    def setWidgetPosition(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

    def setupLayout(self):
        self.setWidgetPosition()

        self.setWindowTitle("관리자 계정 로그인")

        id_label = QLabel("아이디: ")
        pw_label = QLabel("비밀번호: ")

        entry_layout = QGridLayout()
        entry_layout.addWidget(id_label, 0, 0)
        entry_layout.addWidget(self.id_entry, 0, 1)
        entry_layout.addWidget(pw_label, 1, 0)
        entry_layout.addWidget(self.pw_entry, 1, 1)

        button_layout = QGridLayout()
        button_layout.addWidget(self.sign_in, 2, 1)
        button_layout.addWidget(self.sign_up, 2, 2)

        layout = QGridLayout()
        layout.addLayout(entry_layout, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.setContentsMargins(50, 20, 50, 20)

        self.setLayout(layout)

    def signInClicked(self):
        _identification = self.id_entry.text()
        _passwd = self.pw_entry.text()

        user = db.child("admin").child(_identification).get()
        if user.val() is None:
            messagebox = setCriticalMessageBox(self, "존재하지 않는 사용자입니다.")
            self.id_entry.setText('')
            self.pw_entry.setText('')
            return

        val = dict(user.val())

        if val['blocked']:
            messagebox = setCriticalMessageBox(self, "정지된 계정입니다.")
            self.id_entry.setText('')
            self.pw_entry.setText('')
            return

        pw_confirm = val['passWd']

        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            _passwd.encode('utf-8'),
            b64decode(pw_confirm['salt']),
            100000
        )

        if b64decode(pw_confirm['key']) != new_key:
            messagebox = setCriticalMessageBox(self, "비밀번호가 일치하지 않습니다.")
            self.pw_entry.setText('')
            return

        user_data = val.copy()
        user_data['id'] = _identification

        self.login_user_data = user_data

        self.close()

    def signUpClicked(self):
        r = RegisterDialog()
        r.exec_()

        self.id_entry.setText(r.id_entry.text())
        self.pw_entry.setText(r.pw_entry.text())

    def closeEvent(self, event):
        if self.id_entry.text() == '' or self.pw_entry.text() == '':
            event.ignore()
        else:
            event.accept()


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.width = 300
        self.height = 250

        self.id_entry = QLineEdit()
        self.access_code = QLineEdit()

        self.pw_entry = QLineEdit()
        self.pw_entry.setEchoMode(QLineEdit.Password)

        self.pw_confirm_entry = QLineEdit()
        self.pw_confirm_entry.setEchoMode(QLineEdit.Password)

        self.register = "계정 생성하기"
        self.register.clicked.connect(self.register_clicked)

        self.setupLayout()

    @property
    def register(self):
        return self._register

    @register.setter
    def register(self, value):
        self._register = QPushButton(value)

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

        self.setWindowTitle("관리자 계정 회원가입")

        id_label = QLabel("아이디: ")
        pw_label = QLabel("비밀번호: ")
        pw_confirm_label = QLabel("비밀번호 확인: ")
        access_code_label = QLabel("관리자 코드: ")

        entry_layout = QGridLayout()
        entry_layout.addWidget(id_label, 0, 0)
        entry_layout.addWidget(self.id_entry, 0, 1)

        entry_layout.addWidget(pw_label, 1, 0)
        entry_layout.addWidget(self.pw_entry, 1, 1)

        entry_layout.addWidget(pw_confirm_label, 2, 0)
        entry_layout.addWidget(self.pw_confirm_entry, 2, 1)

        entry_layout.addWidget(access_code_label, 3, 0)
        entry_layout.addWidget(self.access_code, 3, 1)

        button_layout = QGridLayout()
        button_layout.addWidget(self.register, 0, 0)

        layout = QGridLayout()
        layout.addLayout(entry_layout, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.setContentsMargins(50, 0, 50, 0)

        self.setLayout(layout)

    @staticmethod
    def make_password(passwd):
        salt = os.urandom(64)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            passwd.encode('utf-8'),
            salt,
            100000
        )

        _passwd = {
            'key': b64encode(key).decode('utf-8'),
            'salt': b64encode(salt).decode('utf-8')
        }
        return _passwd

    def register_clicked(self):
        _identification = self.id_entry.text()
        _access_code = self.access_code.text()

        validation = db.child("admin").child(_identification).get()
        if validation.val():
            messagebox = setCriticalMessageBox(self, "이미 생성된 계정입니다.")
            self.id_entry.setText('')
            self.pw_entry.setText('')
            self.pw_confirm_entry.setText('')
            self.access_code.setText('')
            return

        passwd = self.pw_entry.text()
        passwd_confirm = self.pw_confirm_entry.text()
        if passwd != passwd_confirm:
            messagebox = setCriticalMessageBox(self, "비밀번호가 일치하지 않습니다.")
            self.pw_entry.setText('')
            self.pw_confirm_entry.setText('')
            self.access_code.setText('')
            return

        db.child("admin").child(_identification).update({
            "passWd": self.make_password(passwd),
            "accessCode": _access_code,
            "blocked": False
        })

        self.close()


class AdminDialog(QDialog):
    def __init__(self, parent=None, login_user=None):
        super().__init__(parent)
        print(login_user)

        self.login_user = login_user
        self.access_approval = False

        self.width = 300
        self.height = 200

        self.code_entry = QLineEdit()
        self.code_entry.setEchoMode(QLineEdit.Password)

        self.authenticate = '인증하기'
        self.authenticate.clicked.connect(self.validate_access_code)

        self.setupLayout()

    @property
    def authenticate(self):
        return self._authenticate

    @authenticate.setter
    def authenticate(self, value):
        self._authenticate = QPushButton(value)

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

        self.setWindowTitle("관리자 인증하기")

        code_label = QLabel("접근 코드: ")

        entry_layout = QGridLayout()
        entry_layout.addWidget(code_label, 0, 0)
        entry_layout.addWidget(self.code_entry, 0, 1)

        button_layout = QGridLayout()
        button_layout.addWidget(self.authenticate, 0, 0)

        layout = QGridLayout()
        layout.addLayout(entry_layout, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.setContentsMargins(50, 20, 50, 20)

        self.setLayout(layout)

    def validate_access_code(self):
        _access_code = self.code_entry.text()

        if _access_code != self.login_user["accessCode"]:
            messagebox = setCriticalMessageBox(self, "코드가 일치하지 않습니다.")
            self.code_entry.setText('')
            return

        self.access_approval = True
        self.close()
