from datetime import date
from abc import ABCMeta, abstractmethod


class ScheduleRepository(metaclass=ABCMeta):
    def __init__(self):
        self._query = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @abstractmethod
    def create_schedule_table(self):
        pass

    @abstractmethod
    def insert_schedule(
            self,
            worker_id: int,
            day_option: str,
            work_date: date,
            config_term_count: int,
            schedule_term_idx: int
    ) -> bool:
        pass

    @abstractmethod
    def update_schedule(
            self,
            day_option: str,
            work_date: date,
            schedule_term_idx: int,
            prev_worker_id: int,
            new_worker_id: int
    ) -> bool:
        pass
