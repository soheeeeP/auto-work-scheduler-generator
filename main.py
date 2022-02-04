import sys
from PyQt5.QtWidgets import *

from db import DataBase
from component.app import WindowApplication

from domain.repository.config import ConfigInMemoryRepository
from domain.repository.user import UserInMemoryRepository
from domain.repository.workmode import WorkModeInMemoryRepository
from domain.repository.schedule import ScheduleInMemoryRepository


database = DataBase(db_name='test.db')
database.connect_in_memory_repositories(
        config_repository=ConfigInMemoryRepository(),
        user_repository=UserInMemoryRepository(),
        work_mode_repository=WorkModeInMemoryRepository(),
        schedule_repository=ScheduleInMemoryRepository()
    )
database.create_db_tables()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = WindowApplication(db=database)
    window.show()

    sys.exit(app.exec_())
