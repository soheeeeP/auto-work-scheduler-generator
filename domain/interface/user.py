from typing import List, Tuple, NewType, Union, Dict
from abc import ABCMeta, abstractmethod

# TODO: dict 활용하기
UserData = NewType('UserData', Dict)


class UserRepository(metaclass=ABCMeta):
    def __init__(self):
        self.query = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @abstractmethod
    def print_user_info_from_query(self):
        pass

    @abstractmethod
    def create_default_user_table(self):
        pass

    @abstractmethod
    def get_all_users(self) -> Union[List[UserData], None]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_user_by_name(self, name: str) -> Union[List[UserData], None]:
        pass

    @abstractmethod
    def get_users_by_rank(self, rank: str) -> Union[List[UserData], NameError]:
        pass

    @abstractmethod
    def get_users_by_status(self, status: str) -> Union[List[UserData], NameError]:
        pass

    @abstractmethod
    def insert_new_user(self, user: UserData) -> int:
        pass

    @abstractmethod
    def insert_dummy_users(self, user: List[UserData]):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def delete_all_users(self):
        pass

    @abstractmethod
    def update_user_work_count(self, user_id: int, mode: str, up: bool):
        """
        :param user_id: 객체의 pk
        :param mode: count를 저장할 요일 ("weekday", "holiday")
        :param up: work_count 증가/감소 (True, False)
        """
        pass

    @abstractmethod
    def get_user_id(self, user_data: Dict) -> Union[int, ValueError]:
        pass

    @abstractmethod
    def update_user(self, user_id: int, user_data: Dict):
        pass

    @abstractmethod
    def get_max_work_count(self):
        pass

    @abstractmethod
    def get_min_work_count(self):
        pass

    @abstractmethod
    def get_work_mode_users(self):
        pass
