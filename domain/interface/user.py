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
        """
        쿼리로 읽어온 데이터를 출력하고,
        Type Annotation으로 감싼 객체를 반환한다.
        :return:
            UserData = {
                "id": int,
                "rank": str,
                "name": str,
                "status": str,
                "weekday_work_count": int,
                "holiday_work_count": int
            }
        """
        pass

    @abstractmethod
    def print_users_info_list_from_query(self):
        """
        쿼리로 읽어온 데이터 list를 출력하고,
        Type Annotation으로 감싼 객체의 리스트를 반환한다.
        :return: [ UserData1, UserData2, ... ]
        """
        pass

    @abstractmethod
    def create_default_user_table(self):
        """
        user 테이블을 생성한다.
        :keyword: rank: 계급(이병, 일병, 상병, 병장)
        :keyword: name: 이름
        :keyword: status: 근무 상태 (사수, 부사수)
        :keyword: weekday_work_count: 평일 근무 누적횟수 (default=0)
        :keyword: holiday_work_count: 휴일 근무 누적횟수 (default=0)
        """
        pass

    @abstractmethod
    def get_all_users(self) -> Union[List[UserData], None]:
        """
        쿼리를 수행하여 모든 user 데이터를 반환한다.
        :return: [ UserData1, UserData2, ... ]
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> bool:
        """
        id로 조회한 user 객체 데이터를 반환한다.
        :param user_id: 조회할 사용자 id
        :return: True(성공)
        """
        pass

    @abstractmethod
    def get_user_by_name(self, name: str) -> Union[List[UserData], None]:
        """
        이름으로 조회한 모든 user 객체 데이터 리스트를 반환한다.
        :param name: 검색할 사용자 이름 문자열
        :return: [ UserData1, UserData2, ... ]
        """
        pass

    @abstractmethod
    def get_users_by_rank(self, rank: str) -> Union[List[UserData], NameError]:
        """
        계급으로 조회한 모든 user 객체 데이터 리스트를 반환한다.
        :param rank: 검색할 사용자 계급
        :return: [ UserData1, UserData2, ... ]
        """
        pass

    @abstractmethod
    def get_users_by_status(self, status: str) -> Union[List[UserData], NameError]:
        """
        사용자 상태로 조회한 모든 user 객체 데이터 리스트를 반환한다.
        :param status: 사수 / 부사수
        :return: [ UserData1, UserData2, ... ]
        """
        pass

    @abstractmethod
    def insert_new_user(self, user: UserData) -> int:
        """
        user 객체를 생성한다.
        :param user: 생성할 사용자 정보 ({name, rank, status, weekday_work_count, holiday_work_count})
        :return: 생성한 객체 id
        """
        pass

    @abstractmethod
    def insert_dummy_users(self, user: List[UserData]):
        """
        user 객체를 한꺼번에 생성한다.
        :param user: 생성할 사용자들의 정보가 저장된 list
        :return: 생성한 객체 id list
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        """
        id로 조회한 user 객체를 삭제한다.
        :param user_id: 삭제할 사용자 id
        """
        pass

    @abstractmethod
    def delete_all_users(self):
        """
        user 테이블에 저장된 모든 객체를 삭제한다.
        """
        pass

    @abstractmethod
    def update_user_work_count(self, user_id: int, mode: str, up: bool):
        """
        :param user_id: 사용자 객체 id
        :param mode: count를 저장할 요일 (weekday, holiday)
        :param up: work_count 증가/감소 여부 (True, False)
        """
        pass

    @abstractmethod
    def get_user_id(self, user_data: Dict) -> Union[int, ValueError]:
        """
        조회한 객체의 id를 반환한다.
        :param user_data: 조회할 사용자 정보
        :return: 사용자 객체 id
        """
        pass

    @abstractmethod
    def update_user(self, user_id: int, user_data: Dict):
        """
        id로 조회한 객체를 수정한다.
        :param user_id: 수정할 사용자 객체 id
        :param user_data: 수정할 사용자 정보 ({name, rank, status, weekday_work_count, holiday_work_count})
        """
        pass

    @abstractmethod
    def get_max_work_count(self):
        """
        user 테이블에 저장된 weekday_work_count 칼럼의 최대값을 반환한다.
        """
        pass

    @abstractmethod
    def get_min_work_count(self):
        """
        user 테이블에 저장된 holiday_work_count 칼럼의 최대값을 반환한다.
        """
        pass
