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
        """
        쿼리로 읽어온 데이터를 반환한다.
        :return: { "id", "user_id", "user_name", "start", "end" }
        """
        pass

    @abstractmethod
    def create_exp_datetime_table(self):
        """
        exp_datetime 테이블을 생성한다.
        :keyword: user_id: 사용자 객체 (FK)
        :keyword: start_datetime: 예외 시작시간 (yyyy/MM/dd hh:mm)
        :keyword: end_datetime: 예외 종료시간 (yyyy/MM/dd hh:mm)
        """
        pass

    @abstractmethod
    def insert_exp_datetime(self, user_id: int, start_dt: str, end_dt: str) -> Union[int, None]:
        """
        user_id로 주어진 사용자 객체에 대한 exp_datetime 객체를 생성한다.
        :param user_id: exp_datetime에서 참조할 사용자 객체 id (FK)
        :param start_dt: 예외 시작시간 (yyyy/MM/dd hh:mm)
        :param end_dt: 예외 종료시간 (yyyy/MM/dd hh:mm)
        :return: 생성한 exp_datetime 객체 데이터
        """
        pass

    @abstractmethod
    def update_exp_datetime(self, exp_id: int, start_dt: str, end_dt: str) -> Union[int, None]:
        # todo: 잘못된 접근방법의 메서드. 삭제 요망
        """
        주어진 exp_id를 필드값으로 가지고 있는 exp_datetime 객체의 시작, 종료시간 값을 수정한다.
        :param exp_id: 수정할 exp_datetime 객체의 exp_id
        :param start_dt: 예외 시작시간 (yyyy/MM/dd hh:mm)
        :param end_dt: 예외 종료시간 (yyyy/MM/dd hh:mm)
        :return: 성공할 경우, True 반환
        """
        pass

    @abstractmethod
    def update_exp_datetime_timeline_by_user_id(self, user_id: int, start_dt: str, end_dt: str) -> bool:
        """
        user_id를 필드값으로 가지고 있는 모든 exp_datetime 객체들의 시작, 종료시간 값을 갱신한다.
            #1. renew_user_exp_datetime_timeline() 메서드로 전체 타임라인을 갱신
            #2. 존재하던 모든 exp_datetime 객체들을 삭제
            #3. 갱신된 타임라인 데이터로 exp_datetime 객체를 다시 생성
        :param user_id: exp_datetime에 저장된 사용자 객체 id (FK)
        :param start_dt: 예외 시작시간 (yyyy/MM/dd hh:mm)
        :param end_dt: 예외 종료시간 (yyyy/MM/dd hh:mm)
        :return: 성공할 경우, True 반환
        """
        pass

    @abstractmethod
    def update_exp_datetime_timeline_all_user(self) -> bool:
        """
        오늘 일자를 기준으로 모든 exp_datetime 객체 데이터를 갱신한다.
        :return: 성공할 경우, True 반환
        """
        pass

    @abstractmethod
    def get_all_exp_datetime(self) -> Union[List[Dict], None]:
        """
        모든 exp_datetime 객체 데이터 리스트를 반환한다.
        :return: [ WorkData, WorkData, ... ]
        """
        pass

    @abstractmethod
    def get_exp_datetime(self, exp_id: int) -> Union[Dict, NameError]:
        # todo: 잘못된 접근방법의 메서드. 삭제 요망
        """
        주어진 exp_id에 대한 exp_datetime 객체 데이터를 반환한다.
        :param exp_id: 조회할 exp_id
        :return: WorkData = {"id", "user_id", "user_name", "start", "end" }
        """
        pass

    @abstractmethod
    def delete_all_exp_datetime(self):
        """
        모든 exp_datetime 데이터를 삭제한다.
        """
        pass

    @abstractmethod
    def delete_exp_datetime_by_id(self, exp_id: int) -> Union[int, None]:
        # todo: 잘못된 접근방법의 메서드. 삭제 요망
        """
        exp_id로 조회한 exp_datetime 객체를 삭제한다.
        :param exp_id: 삭제할 exp_id
        :return: 성공할 경우, 쿼리 수행 결과(True)를 반환
        """
        pass

    @abstractmethod
    def delete_exp_datetime_by_user_id(self, user_id: int) -> Union[int, None]:
        """
        user_id로 조회한 모든 exp_datetime 객체들을 삭제한다.
        :param user_id: 조회할 user_id
        :return: 성공할 경우, 쿼리 수행 결과(True)를 반환
        """
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
        # todo: exp_relation_query_record()와 결합한뒤 코드 리팩토링
        """
        쿼리로 읽어온 데이터를 반환한다.
        :return: { "id", "user1_id", "user1_name", "user2_id", "user2_name" }
        """
        pass

    @abstractmethod
    def create_exp_relation_table(self):
        """
        exp_relation 테이블을 생성한다.
        :keyword: user1_id: 예외관계를 설정할 사용자1 객체 id (FK)
        :keyword: user2_id: 예외관계를 설정할 사용자2 객체 id (FK)
        """
        pass

    @abstractmethod
    def insert_exp_relation_by_id(self, user1_id: int, user2_id) -> bool:
        # todo: MultipleObjectsExist에 대한 예외처리 필요
        """
        user_id로 주어진 두 사용자 객체에 대한 exp_relation 객체를 생성한다.
        :param: user1_id: 예외관계를 설정할 사용자1 객체 id (FK)
        :param: user2_id: 예외관계를 설정할 사용자2 객체 id (FK)
        :return: 성공시, 쿼리 수행 결과(True)를 반환
        """
        pass

    @abstractmethod
    def insert_exp_relation_by_name(self, user1_name: str, user2_name: str) -> bool:
        """
        이름으로 주어진 두 사용자에 대한 exp_relation 객체를 생성한다.
        :param user1_name: 예외관계를 설정할 사용자1 이름
        :param user2_name: 예외관계를 설정할 사용자2 이름
        :return: 성공시, 쿼리 수행 결과(True)를 반환
        """
        pass

    @abstractmethod
    def get_exp_relation_by_user_id_set(self, user1_id: int, user2_id: int) -> Union[Dict, None]:
        """
        user_id로 주어진 두 사용자 객체에 대한 exp_relation 객체 데이터를 반환한다.
        객체는 유일하게 존재한다.
        :param user1_id: 예외관계를 조회할 사용자1 id (FK)
        :param user2_id: 예외관계를 조회할 사용자2 id (FK)
        :return: { "id", "user1_id", "user1_name", "user2_id", "user2_name" }
        """
        pass

    @abstractmethod
    def get_exp_relation_by_user_name_set(self, user1_name: str, user2_name: str) -> Union[Dict, None]:
        """
        이름으로 주어진 두 사용자 객체에 대한 exp_relation 객체 데이터를 반환한다.
        객체는 유일하게 존재한다.
        :param user1_id: 예외관계를 조회할 사용자1 이름
        :param user2_id: 예외관계를 조회할 사용자2 이름
        :return: { "id", "user1_id", "user1_name", "user2_id", "user2_name" }
        """
        pass

    @abstractmethod
    def get_all_exp_relation(self) -> Union[List[Dict], None]:
        """
        모든 exp_relation 객체 데이터 리스트를 반환한다.
        :return: [ RelationData, RelationData, ... ]
        """
        pass

    @abstractmethod
    def delete_exp_relation_by_user_id_set(self, user1_id: int, user2_id: int) -> bool:
        """
        사용자 id로 조회되는 exp_relation 객체를 삭제한다.
        :param user1_id: 삭제할 exp_datetime 객체의 user1_id
        :param user2_id: 삭제할 exp_datetime 객체의 user2_id
        :return: 삭제된 객체가 존재할 경우 True, 존재하지 않을 경우 False
        """
        pass

    @abstractmethod
    def delete_exp_relation_by_user_name_set(self, user1_name: int, user2_name: set) -> bool:
        """
        사용자 이름에 대한 사용자 id로 조회되는 exp_relation 객체를 삭제한다.
        :param user1_name: 삭제할 exp_datetime 객체의 user1_id 사용자 객체 이름 필드값
        :param user2_name: 삭제할 exp_datetime 객체의 user2_id 사용자 객체 이름 필드값
        :return: 삭제된 객체가 존재할 경우 True, 존재하지 않을 경우 False
        """
        pass

    @abstractmethod
    def delete_all_exp_relation(self) -> bool:
        """
        모든 exp_relation 데이터를 삭제한다.
        :return: 삭제된 객체가 1개 이상 존재할 경우 True, 존재하지 않을 경우 False
        """
        pass
