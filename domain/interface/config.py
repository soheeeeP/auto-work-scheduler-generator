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
        pass

    @abstractmethod
    def insert_config(self) -> bool:
        pass

    @abstractmethod
    def get_config(self) -> Tuple[int, int, bool]:
        pass

    @abstractmethod
    def set_config_term_count(self, term_count: int):
        pass

    @abstractmethod
    def set_config_worker_per_term(self, worker_per_term: int):
        pass

    @abstractmethod
    def set_config_assistant_mode(self, assistant_mode: bool):
        pass
