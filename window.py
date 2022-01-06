from tkinter import *


class Window(object):
    def __init__(self):
        self._window = None
        self._menu = None

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

        width, height = 720, 540
        start_w = int(self._window.winfo_screenwidth() - width) / 2
        start_h = int(self._window.winfo_screenheight() - height) / 2
        self._window.geometry(f"{width}x{height}+{int(start_w)}+{int(start_h)}")
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
        menu.add_command(label='시간당 근무 인원수 설정')
        menu.add_separator()
        menu.add_command(label='사수/부사수 옵션 설정')
        menu.add_separator()
        menu.add_command(label='근무 교대 텀 설정')
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
