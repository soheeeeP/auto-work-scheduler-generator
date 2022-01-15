from datetime import date

from domain.interface.schedule import ScheduleRepository


class ScheduleInMemoryRepository(ScheduleRepository):
    def create_schedule_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS schedule (
                schedule_id INTEGER primary key autoincrement,
                worker_id INTEGER,
                day_option VARCHAR(30) NOT NULL,
                date DATE NOT NULL,
                term_idx INTEGER CHECK (term_idx > 0 and term_idx < 24) NOT NULL, 
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                foreign key (worker_id) REFERENCES user(id)
            )
            """
        )

    def insert_schedule(
            self,
            worker_id: int,
            day_option: str,
            work_date: date,
            config_term_count: int,
            schedule_term_idx: int
    ):
        self.query.prepare(
            """
            INSERT INTO 
                schedule(worker_id, day_option, date, term_idx, start_time, end_time) 
                VALUES (:worker_id, :day_option, :date, :term_idx, :start_time, :end_time);
            """
        )
        time_section = 24 // config_term_count
        self.query.bindValue(":worker_id", worker_id)
        self.query.bindValue(":day_option", day_option)
        self.query.bindValue(":date", date)
        self.query.bindValue(":term_idx", schedule_term_idx)
        self.query.bindValue(":start_time", time_section * (schedule_term_idx - 1))
        self.query.bindValue(":end_time", time_section * schedule_term_idx)
        self.query.exec_()

    def update_schedule(
            self,
            day_option: str,
            work_date: date,
            schedule_term_idx: int,
            prev_worker_id: int,
            new_worker_id: int
    ):
        # TODO: db.transaction() 적용하기
        self.query.prepare(
            """
            UPDATE schedule SET worker_id = (SELECT id FROM user WHERE id=(:new_worker_id) IS NOT NULL)
                WHERE worker_id = (SELECT id FROM user WHERE id=(:prev_worker_id) IS NOT NULL) AND 
                    day_option = (:day_option) AND
                    date = (:date) AND
                    term_idx = (:term_idx);
            """
        )
        self.query.bindValue(":new_worker_id", new_worker_id)
        self.query.bindValue(":prev_worker_id", prev_worker_id)
        self.query.bindValue(":day_option", day_option)
        self.query.bindValue(":date", work_date)
        self.query.bindValue(":term_idx", schedule_term_idx)
        self.query.exec_()

        # TODO: repository단위로 query method 분리하기 (user_repository.update_user_work_count)
        self.query.prepare(f"""UPDATE user SET work_count = work_count - 1 WHERE id = (:id)""")
        self.query.bindValue(":id", prev_worker_id)
        self.query.exec_()

        self.query.prepare(f"""UPDATE user SET work_count = work_count + 1 WHERE id = (:id)""")
        self.query.bindValue(":id", new_worker_id)
        self.query.exec_()
