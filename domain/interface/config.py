from typing import Tuple
from abc import ABCMeta, abstractmethod


class ConfigRepository(metaclass=ABCMeta):
    def __init__(self):
        self._query = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @abstractmethod
    def create_config_table(self):
        """
        config db 테이블을 생성한다.
        :keyword: term_count: 교대제 설정값 (default=3)
        :keyword: worker_per_term: 시간당 근무 인원수 (default=1)
        :keyword: assistant_mode: 사수/부사수 근무모드 (default=False)
        """
        pass

    @abstractmethod
    def insert_config(self) -> bool:
        """
        프로그램 기본 설정값을 config 객체로 생성한다.
        """
        pass

    @abstractmethod
    def get_config(self) -> Tuple[int, int, bool]:
        """
        프로그램 설정값을 읽어서 리턴한다.
        설정값이 세팅되어 있지 않으면, default value로 config 객체를 생성하고 리턴한다.
        :return: (term_count, worker_per_term, assistant_mode)
        """
        pass

    @abstractmethod
    def set_config_term_count(self, term_count: int):
        """
        교대제 설정값을 변경한다.
        :param term_count: 교대제 (1, 2, 3, 4, 12)
        """
        pass

    @abstractmethod
    def set_config_worker_per_term(self, worker_per_term: int):
        """
        시간당 근무 인원수 설정값을 변경한다.
        :param worker_per_term: 시간당 근무 인원수 (1, 2, 3)
        """
        pass

    @abstractmethod
    def set_config_assistant_mode(self, assistant_mode: bool):
        """
        사수/부사수 근무모드 설정값을 변경한다.
        :param assistant_mode: 사수/부사수 모드 (True, False)
        :return:
        """
        pass
