from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction

from component.window import SubWindow, DBWindow, ProgramOptionWindow
from component.dialog import LogInDialog


class WindowApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        dialog = LogInDialog()
        dialog.exec_()

        self.width = 720
        self.height = 540

        self.setupLayout()

        self.show()

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

    def setupLayout(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x() - int(self.width / 2), center.y() - int(self.height / 2), self.width, self.height)

        self.setWindowTitle('Auto work-scheduler generator for Army Soldiers')

        self.setupMenuBar()

    def workerPerTerm(self):
        SubWindow(self, 'worker').show()

    def assistantMode(self):
        SubWindow(self, 'assistant').show()

    def workShiftTerm(self):
        SubWindow(self, 'work_shift').show()

    def registerDB(self):
        DBWindow(self, 'register').show()

    def editDB(self):
        DBWindow(self, 'edit/view').show()

    def deleteDB(self):
        DBWindow(self, 'delete').show()

    def outsideOption(self):
        ProgramOptionWindow(self, 'outside').show()

    def exceptionOption(self):
        ProgramOptionWindow(self, 'exception').show()

    def specialRelationOption(self):
        ProgramOptionWindow(self, 'special_relation').show()
