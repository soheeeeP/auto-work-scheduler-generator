from datetime import datetime
from typing import List, NewType, Tuple, Dict, Union
from abc import ABCMeta, abstractmethod

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
    def print_user_work_info_from_query(self):
        """
        쿼리로 읽어온 데이터를 반환한다.
        :return: user_id, { rank, name, status, weekday_work_count, holiday_work_count }
        """
        pass

    @abstractmethod
    def create_work_mode_table(self, term_count: int):
        # todo: 하나의 user_id에 대해서 하나의 workmode 객체가 존재해야 한다. (DoesExist에 대한 예외처리 필요)
        """
        workmode 테이블을 생성한다.
        :param term_count: config에 저장된 교대제 설정값. weekday_#, holiday_# 컬럼의 갯수를 정하기 위해 사용되는 변수.
        :keyword: user_id: 사용자 객체 (FK)
        :keyword: work_mode: 근무자 편성 여부 (on, off)
        :keyword: weekday_{term_count} 평일 시간대별 근무여부
                예시) term_count = 3, weekday_1 = 0인 workmode 객체가 존재한다면,
                     평일 0~8시에는 user_id로 매핑된 사용자에 대한 근무편성을 제외한다.
        :keyword: holiday_{term_count}: 휴일 시간대별 근무 여부
        """
        pass

    @abstractmethod
    def drop_work_mode_table(self):
        """
        workmode 테이블을 삭제한다.
        :return:
        """
        pass

    @abstractmethod
    def insert_user_work_mode(self, user_id: int, option: WorkData):
        """
        user_id로 주어진 사용자 객체에 대한 workmode 객체를 생성한다.
        :param user_id: workmode에서 참조할 사용자 객체 id (FK)
        :param option: 생성할 workmode 데이터 dict(work_mode, weekday_#, holiday_#)
        """
        pass

    @abstractmethod
    def update_user_work_mode(self, user_id: int, option: WorkData):
        """
        주어진 user_id를 필드값으로 가지고 있는 workmode 객체를 수정한다.
        :param user_id: 수정할 workmode 객체의 user_id
        :param option: 수정할 workmode 데이터 dict(work_mode, weekday_#, holiday_#)
        """
        pass

    @abstractmethod
    def update_users_list_work_mode(self, options: List[WorkData]):
        """
        workmode 객체를 한번에 수정한다.
        :param options: 수정할 workmode 데이터 dict로 이루어진 list
        :return:
        """
        pass

    @abstractmethod
    def get_all_users_work_mode_columns(self, term_count: int) -> Union[List[Dict], None]:
        """
        모든 사용자 객체에 대한 workmode 데이터를 반환한다.
        :param term_count: config에 저장된 교대제 설정값.
        :return:
            [
                {
                    "id", "rank", "status", "weekday_work_count", "holiday_work_count",
                    "workmode", "weekday_", "holiday_"
                },
                { ... },
                { ... },
            ]
        """
        pass

    @abstractmethod
    def get_user_work_mode_column(self, user_id: int, term_count: int) -> Union[Dict, NameError]:
        """
        user_id로 주어진 사용자 객체에 대한 workmode 데이터를 반환한다.
        :param user_id: 조회할 workmode 객체의 user_id
        :param term_count: config에 저장된 교대제 설정값.
        :return:
            [
                {
                    "rank", "status", "work_count", "holiday_work_count",
                    "workmode", "weekday_", "holiday_"
                },
                { ... },
                { ... },
            ]
        """
        pass

    @abstractmethod
    def get_work_mode_users(self) -> Union[Dict, None]:
        """
        work_mode가 'on'으로 설정되어 있는 모든 객체를 반환한다.
        :return:
        """
        pass

    @abstractmethod
    def drop_term_count_related_columns(self, term_count: int) -> bool:
        """
        존재하던 workmode 테이블을 삭제하고, 새로 주어진 term_count를 인자로 하는 workmode 테이블을 다시 생성한다.
        :param term_count: config에 저장된 교대제 설정값. weekday_#, holiday_# 컬럼의 갯수를 정하기 위해 사용되는 변수.
        :return: 성공할 경우, 쿼리 수행 결과(True)를 반환
        """
        pass
