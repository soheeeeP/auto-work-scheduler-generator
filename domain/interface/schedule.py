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
        """
        schedule 테이블을 생성한다.
        :keyword: worker_id: 사용자 객체 (FK)
        :keyword: day_option: 근무요일 (weekday, holiday)
        :keyword: date: 근무일자(yyyy-mm-dd)
        :keyword: term_idx: 근무 편성 idx (0 <= term_idx < 24)
        :keyword: start_time: 근무 시작 시간 ( 24 / 근무교대 텀 * (term_idx - 1) )
        :keyword: end_time: 근무 종료 시간 ( 24 / 근무교대 텀 * term_idx )
        """
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
        """
        schedule 객체를 생성한다.
        :param worker_id: 사용자 객체 (FK)
        :param day_option: 근무요일 (weekday, holiday)
        :param work_date: 근무일자(yyyy-mm-dd)
        :param config_term_count: 근무교대 텀
        :param schedule_term_idx: 근무 편성 idx (0 <= term_idx < 24)
        :return:
        """
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
        """
        schedule 객체의 worker_id 필드를 수정한다.
        특정 일자, 시간대의 근무자를 prev_worker_id 사용자 객체에서 new_worker_id 사용자 객체로 변경한다.
        :param day_option: 근무요일 (weekday, holiday)
        :param work_date: 근무일자(yyyy-mm-dd)
        :param schedule_term_idx: 근무 편성 idx (0 <= term_idx < 24)
        :param prev_worker_id: 기존 근무자 id
        :param new_worker_id: 새로운 근무자 id
        :return: 수정한 schedule 객체 데이터
        """
        pass
