from typing import List, NewType, Tuple, Dict
from abc import ABCMeta, abstractmethod


class WorkType:
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
    def update_user_work_mode(self, option: WorkType.WorkData):
        pass

    @abstractmethod
    def update_users_list_work_mode(self, options: List[WorkType.WorkData]):
        pass
