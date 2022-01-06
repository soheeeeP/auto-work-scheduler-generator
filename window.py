from tkinter import *


# TODO: Window, Menu, Frame 별도의 class로 분리하기
class Window(object):
    def __init__(self, db):
        self.db = db
        self._window = None
        self._menu = None

        self.width = 720
        self.height = 540

    def __del__(self):
        if self._window:
            self._window.quit()
            self._window.destroy()

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, title):
        self._window = Tk()
        self._window.title(title)

        start_w = int(self._window.winfo_screenwidth() - self.width) / 2
        start_h = int(self._window.winfo_screenheight() - self.height) / 2
        self._window.geometry(f"{self.width}x{self.height}+{int(start_w)}+{int(start_h)}")
        self._window.resizable(False, False)

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, window):
        self._menu = Menu(window)

    def start_window(self):
        self.window = 'Auto work-scheduler generator for Army Soldiers'
        self.menu = self._window

        self.create_window_menu_bar()

        self._window.config(menu=self._menu)
        self._window.mainloop()

    def main_option_menu(self) -> Menu:
        menu = Menu(self._menu, tearoff=0)
        menu.add_command(label='시간당 근무 인원수 설정', command=lambda: self.worker_per_term_frame())
        menu.add_separator()
        menu.add_command(label='사수/부사수 옵션 설정', command=lambda: self.assistant_mode_on_off_frame())
        menu.add_separator()
        menu.add_command(label='근무 교대 텀 설정', command=lambda: self.work_shift_term_frame())
        return menu

    def db_menu(self) -> Menu:
        menu = Menu(self._menu, tearoff=0)
        menu.add_command(label='인원DB 등록')
        menu.add_command(label='인원DB 수정')
        menu.add_command(label='인원DB 조회')
        menu.add_separator()
        menu.add_command(label='인원 특수 관계도 조회')
        return menu

    def exceptional_option_menu(self) -> Menu:
        menu = Menu(self._menu, tearoff=0)
        menu.add_command(label='영외인원 등록 및 수정')
        menu.add_command(label='열외인원 등록 및 수정')
        menu.add_separator()
        menu.add_command(label='특수 관계 등록 및 수정')
        return menu

    def save_menu(self) -> Menu:
        menu = Menu(self._menu, tearoff=0)
        menu.add_command(label='근무표 저장')
        menu.add_command(label='근무카운트 저장')
        return menu

    def create_window_menu_bar(self):
        self._menu.add_cascade(label='설정', menu=self.main_option_menu())
        self._menu.add_cascade(label='DB 생성/조회', menu=self.db_menu())
        self._menu.add_cascade(label='추가사항', menu=self.exceptional_option_menu())
        self._menu.add_cascade(label='저장', menu=self.save_menu())

    def spinbox_value_validator(self, value):
        print(value)
        if value.isdigit() and 0 <= int(value) <= 5:
            return True
        return False

    def spinbox_frame(self, message, min_range, max_range):
        frame = Toplevel()
        frame.geometry(
            f"{int(self.width / 2)}x{int(self.height / 2)}"
            f"+{self._window.winfo_x() + int(self.width / 4)}+{self._window.winfo_y() + int(self.height / 4)}"
        )
        label = Label(frame, text=message, height=4).pack()

        validate_command = (frame.register(self.spinbox_value_validator), "%P")
        spinbox = Spinbox(
            frame,
            from_=min_range,
            to=max_range,
            validate='all',
            validatecommand=validate_command
        )
        spinbox.pack()

        # TODO: db연동하여 입력받은 옵션값 저장하기
        Button(frame, text='저장하기', command=frame.destroy).pack()

    def radiobutton_frame(self):
        pass

    def worker_per_term_frame(self):
        # TODO: spinbox frame에 default로 db의 worker_per_term값이 뜨도록 설정
        self.spinbox_frame(message="시간당 근무 인원 수(0 ~ 5)를 입력해주세요", min_range=0, max_range=5)

    def assistant_mode_on_off_frame(self):
        # TODO: radio frame에 default로 db의 assistant_mode가 체크되어 있도록 설정
        self.radiobutton_frame()

    def work_shift_term_frame(self):
        # TODO: spinbox frame에 default로 db의 term_count값이 뜨도록 설정
        self.spinbox_frame(message="근무 교대 횟수(0 ~ 24)를 입력해주세요", min_range=0, max_range=24)
