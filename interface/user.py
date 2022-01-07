from abc import ABCMeta, abstractmethod


class UserRepository(metaclass=ABCMeta):
    @abstractmethod
    def create_default_user_table(self):
        pass

    @abstractmethod
    def add_term_related_columns_in_user(self):
        pass

    @abstractmethod
    def drop_term_related_columns_in_user(self):
        pass

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_by_name(self):
        pass

    @abstractmethod
    def set_user_name(self):
        pass

    @abstractmethod
    def get_user_by_rank(self):
        pass

    @abstractmethod
    def set_user_rank(self):
        pass

    @abstractmethod
    def get_user_by_status(self):
        pass

    @abstractmethod
    def set_user_status(self):
        pass

    @abstractmethod
    def insert_new_user(self):
        pass

    @abstractmethod
    def insert_dummy_users(self):
        pass

    @abstractmethod
    def delete_user(self):
        pass

    @abstractmethod
    def delete_all_users(self):
        pass
