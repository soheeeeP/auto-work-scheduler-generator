from abc import ABCMeta, abstractmethod
from typing import List, Dict, Union


class DateTimeExceptionRepository(metaclass=ABCMeta):
    ymd_format = "yyyy/MM/dd"
    hm_format = "hh:mm"

    def __init__(self):
        self._query = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @abstractmethod
    def print_exp_info_from_query(self) -> Dict:
        pass

    @abstractmethod
    def create_exp_datetime_table(self):
        pass

    @abstractmethod
    def insert_exp_datetime(self, user_id: int, start_dt: str, end_dt: str) -> Union[int, None]:
        pass

    @abstractmethod
    def update_exp_datetime(self, exp_id: int, start_dt: str, end_dt: str) -> Union[int, None]:
        pass

    @abstractmethod
    def update_exp_datetime_timeline_by_user_id(self, user_id: int, start_dt: str, end_dt: str) -> bool:
        pass

    @abstractmethod
    def update_exp_datetime_timeline_all_user(self) -> bool:
        pass

    @abstractmethod
    def get_all_exp_datetime(self) -> Union[List[Dict], None]:
        pass

    @abstractmethod
    def get_exp_datetime(self, exp_id: int) -> Union[Dict, NameError]:
        pass

    @abstractmethod
    def delete_all_exp_datetime(self):
        pass

    @abstractmethod
    def delete_exp_datetime_by_id(self, exp_id: int) -> Union[int, None]:
        pass

    @abstractmethod
    def delete_exp_datetime_by_user_id(self, user_id: int) -> Union[int, None]:
        pass


class RelationExceptionRepository(metaclass=ABCMeta):
    def __init__(self):
        self._query = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @abstractmethod
    def print_from_query(self, col_idx: Dict) -> Dict:
        pass

    @abstractmethod
    def create_exp_relation_table(self):
        pass

    @abstractmethod
    def insert_exp_relation_by_id(self, user1_id: int, user2_id) -> bool:
        pass

    @abstractmethod
    def insert_exp_relation_by_name(self, user1_name: str, user2_name: str) -> bool:
        pass

    @abstractmethod
    def get_exp_relation_by_user_id_set(self, user1_id: int, user2_id: int) -> Union[Dict, None]:
        pass

    @abstractmethod
    def get_exp_relation_by_user_name_set(self, user1_name: str, user2_name: str) -> Union[Dict, None]:
        pass

    @abstractmethod
    def get_all_exp_relation(self) -> Union[List[Dict], None]:
        pass

    @abstractmethod
    def delete_exp_relation_by_user_id_set(self, user1_id: int, user2_id: int) -> bool:
        pass

    @abstractmethod
    def delete_exp_relation_by_user_name_set(self, user1_name: int, user2_name: set) -> bool:
        pass

    @abstractmethod
    def delete_all_exp_relation(self) -> bool:
        pass
