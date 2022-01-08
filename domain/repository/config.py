from typing import Tuple

from domain.interface.config import ConfigRepository


class ConfigInMemoryRepository(ConfigRepository):
    def create_config_table(self):
        """
            term_count: 교대제 설정값 (default=3)
            worker_per_term: 시간당 근무 인원수 (default=1)
            assistant_mode: 사수/부사수 근무모드 (default=False)
        """
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS config (
                id INTEGER primary key autoincrement,
                term_count INTEGER DEFAULT 3,
                worker_per_term INTEGER DEFAULT 1,
                assistant_mode BIT DEFAULT 0
            )
            """
        )

    def insert_config(self):
        self.query.exec_(
            """INSERT INTO config (term_count, worker_per_term, assistant_mode) VALUES (3, 1, 0)"""
        )

    def get_config(self) -> Tuple[int, int, bool]:
        self.query.exec_("SELECT * FROM config")
        if not self.query.first():
            self.insert_config()
            self.query.exec_("SELECT * FROM config")

        self.query.next()
        term_count, worker_per_term, assistant_mode = self.query.value(1), self.query.value(2), self.query.value(3)
        return term_count, worker_per_term, bool(assistant_mode)

    def set_config_term_count(self, term_count: int):
        self.query.exec_(
            f"""
            UPDATE config SET term_count = {term_count} 
            WHERE id = (SELECT id FROM config ORDER BY id limit 1)
            """
        )

    def set_config_worker_per_term(self, worker_per_term: int):
        self.query.exec_(
            f"""
            UPDATE config SET worker_per_term = {worker_per_term} 
            WHERE id = (SELECT id FROM config ORDER BY id limit 1)
            """
        )

    def set_config_assistant_mode(self, assistant_mode: bool):
        self.query.exec_(
            f"""
            UPDATE config SET assistant_mode = {assistant_mode} 
            WHERE id = (SELECT id FROM config ORDER BY id limit 1)
            """
        )
