from typing import List, Tuple, TypeVar, NewType, Union
from abc import ABCMeta, abstractmethod


class UserType(object):
    # UserInfo = NewType('UserInfo', Tuple[str])
    # UserWeekDayTerm = NewType('UserDayTerm', Tuple[bool])
    # UserHolidayTerm = NewType('UserHolidayTerm', Tuple[bool])
    UserData = NewType('UserData', List[Tuple])


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
    def get_all_users(self) -> Union[List[UserType.UserData], None]:
        pass

    @abstractmethod
    def get_user_by_name(self, name: str) -> Union[UserType.UserData, NameError]:
        pass

    @abstractmethod
    def set_user_name(self, name: str):
        pass

    @abstractmethod
    def get_users_by_rank(self, rank: str) -> Union[List[UserType.UserData], NameError]:
        pass

    @abstractmethod
    def set_user_rank(self, rank: str):
        pass

    @abstractmethod
    def get_users_by_status(self, status: str) -> Union[List[UserType.UserData], NameError]:
        pass

    @abstractmethod
    def set_user_status(self, status: str):
        pass

    @abstractmethod
    def insert_new_user(self, data: UserType.UserData):
        pass

    @abstractmethod
    def insert_dummy_users(self, data: List[UserType.UserData]):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def delete_all_users(self):
        pass
