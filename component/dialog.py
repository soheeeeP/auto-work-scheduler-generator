from PyQt5.QtWidgets import QPushButton, QLineEdit, QGridLayout, QDialog, QLabel, QDesktopWidget, QMessageBox


class LogInDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.width = 300
        self.height = 200

        self.id_entry = QLineEdit()
        self.pw_entry = QLineEdit()

        self.sign_in = "로그인"
        self.sign_up = "회원가입"
        self.sign_in.clicked.connect(self.signInClicked)
        self.sign_up.clicked.connect(self.signUpClicked)

        self.setupLayout()

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

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

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
        self.window().close()
        """
        1. id, password 로 관리자 조회
        2. 일치하면 로그인, 메인 메뉴 접근
            (로그인하지 않은 경우, 메뉴 접근 제한)
        3. 일치하지 않으면 QMessageBox.warning
        """

    def signUpClicked(self):
        r = RegisterDialog()
        r.exec_()

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
        self.pw_entry = QLineEdit()
        self.pw_confirm_entry = QLineEdit()
        self.access_code = QLineEdit()

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

    def register_clicked(self):
        passwd = self.pw_entry.text()
        passwd_confirm = self.pw_confirm_entry.text()
        if passwd != passwd_confirm:
            QMessageBox.critical(self, "QMessageBox", "비밀번호가 일치하지 않습니다.", QMessageBox.Close)

        identification = self.id_entry.text()
        code = self.access_code.text()

        """
        1. identification 중복 여부 확인
        2. password 암호화
        3. 계정 생성
        """

        self.close()
