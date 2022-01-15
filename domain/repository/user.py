from typing import List, Tuple, Union

from domain.interface.user import UserRepository, UserType


class UserInMemoryRepository(UserRepository):
    def print_user_info_from_query(self):
        columns_cnt = self.query.record().count()
        term_columns_cnt = int((columns_cnt - 4) / 2) + 4

        user_id, rank, name, status = \
            self.query.value(0), \
            self.query.value(1), \
            self.query.value(2), \
            self.query.value(3)

        data = [
            (user_id, rank, name, status),
            tuple(self.query.value(i) for i in range(4, term_columns_cnt)),
            tuple(self.query.value(i) for i in range(term_columns_cnt, columns_cnt))
        ]
        return UserType.UserData(data)

    def create_default_user_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS user (
                id INTEGER primary key autoincrement,
                rank VARCHAR (30) NOT NULL,
                name VARCHAR (30) NOT NULL,
                status VARCHAR (30) NOT NULL DEFAULT 'Default'
            )
            """
        )

    def get_all_users(self) -> Union[List[UserType.UserData], None]:
        self.query.exec_("SELECT * FROM user")
        if not self.query.first():
            return None

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def get_user_by_name(self, name: str) -> Union[UserType.UserData, NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE name='{name}';""")
        if not self.query.first():
            raise NameError(f'user whose name is {name} does not exist')

        return self.print_user_info_from_query()

    def set_user_name(self, name: str):
        pass

    def get_users_by_rank(self, rank: str) -> Union[List[UserType.UserData], NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE rank='{rank}';""")
        if not self.query.first():
            raise NameError(f'user whose rank is {rank} does not exist')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def set_user_rank(self, rank: str):
        pass

    def get_users_by_status(self, status: str) -> Union[List[UserType.UserData], NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE status='{status}';""")
        if not self.query.first():
            raise NameError(f'user whose status is {status} does not exist')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def set_user_status(self, status: str):
        pass

    def insert_new_user(self, data: UserType.UserData):
        pass

    def insert_dummy_users(self, data: List[UserType.UserData]):
        pass

    def delete_user(self, user_id: int):
        self.query.exec_(
            f"""
            DELETE FROM user WHERE id='{user_id}' AND EXISTS (SELECT * FROM user WHERE id='{user_id}');
            """
        )

    def delete_all_users(self):
        self.query.exec_("""DELETE FROM USER;""")
