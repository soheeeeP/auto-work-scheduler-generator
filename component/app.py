from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction

from component.window import SubWindow, DBWindow
from component.dialog import LogInDialog

from db import database


class WindowApplication(QMainWindow):
    db = database

    def __init__(self):
        super().__init__()

        dialog = LogInDialog()
        dialog.exec_()

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
        workShiftTermMenu.triggered.connect(self.work_shift_term_frame)

        db_menu = menu_bar.addMenu("DB 생성/조회")

        registerDBMenu = QAction("인원DB 등록", self)
        db_menu.addAction(registerDBMenu)
        registerDBMenu.triggered.connect(self.register_db)

        editviewDBMenu = QAction("인원DB 수정 및 조회", self)
        db_menu.addAction(editviewDBMenu)
        editviewDBMenu.triggered.connect(self.edit_db)

        deleteDBMenu = QAction("인원DB 삭제", self)
        db_menu.addAction(deleteDBMenu)
        deleteDBMenu.triggered.connect(self.delete_db)

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

        self.term_count, self.worker_per_term, self.assistant_mode \
            = self._db.config_repository.get_config()
        self.show()

    # TODO: min_value, max_value 수정하기
    def worker_per_time_frame(self):
        SubWindow(self, 'worker', self._db, self.worker_per_term).show()

    def assistant_mode_frame(self):
        SubWindow(self, 'assistant', self._db, self.assistant_mode).show()

    def work_shift_term_frame(self):
        SubWindow(self, 'work_shift', self._db, self.term_count).show()

    def register_db(self):
        DBWindow(self, 'register', self._db).show()

    def edit_db(self):
        DBWindow(self, 'edit/view', self._db).show()

    def delete_db(self):
        DBWindow(self, 'delete', self._db).show()
