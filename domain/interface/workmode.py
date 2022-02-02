from typing import List, NewType, Tuple, Dict, Union
from abc import ABCMeta, abstractmethod

WorkData = NewType('WorkData', Dict)


class WorkModeRepository(metaclass=ABCMeta):
    def __init__(self):
        self._query = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @abstractmethod
    def create_work_mode_table(self, term_count: int):
        pass

    @abstractmethod
    def drop_work_mode_table(self):
        pass

    @abstractmethod
    def insert_user_work_mode(self, user_id: int, option: WorkData):
        pass

    @abstractmethod
    def update_user_work_mode(self, user_id: int, option: WorkData):
        pass

    @abstractmethod
    def update_users_list_work_mode(self, options: List[WorkData]):
        pass

    @abstractmethod
    def get_all_users_work_mode_columns(self, term_count: int) -> Union[List[Dict], None]:
        pass

    @abstractmethod
    def get_user_work_mode_column(self, user_id: int, term_count: int) -> Union[Dict, NameError]:
        pass
