import operator

from main import database


class WorkSchedulerGenerator:
    db = database

    def __init__(self):
        self.term_count, self.worker_per_term, self.assistant_mode = self.db.config_repository.get_config

        self.weekday_workers = "weekday"
        self.holiday_workers = "holiday"

        if self.assistant_mode:
            self.weekday_T, w_seniorLeft, w_juniorLeft = self.assistant_scheduler(queue=self.weekday_workers, days_cnt=5)
            w_workersLeft = [w_seniorLeft, w_juniorLeft]

            self.holiday_T, h_seniorLeft, h_juniorLeft = self.assistant_scheduler(queue=self.holiday_workers, days_cnt=2)
            h_workersLeft = [h_seniorLeft, h_juniorLeft]
        else:
            self.weekday_T, w_workersLeft = self.non_assistant_scheduler(queue=self.weekday_workers, days_cnt=5)
            self.holiday_T, h_workersLeft = self.non_assistant_scheduler(queue=self.holiday_workers, days_cnt=2)

    @property
    def weekday_workers(self):
        return self._weekday_workers

    @weekday_workers.setter
    def weekday_workers(self, value):
        self._weekday_workers = self.get_workers(day=value)

    @property
    def holiday_workers(self):
        return self._holiday_workers

    @holiday_workers.setter
    def holiday_workers(self, value):
        self._holiday_workers = self.get_workers(day=value)

    def get_workers(self, day):
        sum_count = 0
        max_work_count = self.db.work_mode_repository.get_max_work_count()[day]
        key = "weekday" if day == "weekday" else "holiday"

        users = self.db.user_repository.get_work_mode_users()

        users_work_count = {}
        for u in users:
            label = f"{u['id']}|{u['status'].lower()}"
            diff = max_work_count - u[key]
            if diff > 0:
                sum_count += diff
                users_work_count[label] = diff

        avg_count = sum_count // len(users_work_count)

        workers = {}
        for k, v in users_work_count.items():
            if avg_count <= v:
                workers[k] = v

        workers_queue = sorted(workers.items(), key=operator.itemgetter(1))
        return workers_queue

    def generate_work_table(self, queue, table, days_cnt, worker_per_term):
        total_needed_workers = (days_cnt * self.term_count) * worker_per_term

        while sum(q[1] for q in queue) > 0:
            # TODO: table이 꽉 찬 경우, break (dp로 이차원 합 계산)
            for worker in queue:
                worker_key, work_value = worker[0], worker[1]
                if work_value == 0:
                    continue

                if work_value < total_needed_workers:
                    cnt = work_value
                else:
                    cnt = total_needed_workers
                    work_value -= total_needed_workers

                term = total_needed_workers // cnt
                work_cnt = 0
                idx = 0
                bias, bias_mode = 0, False

                while idx < days_cnt * self.term_count:
                    if work_cnt == cnt:
                        break

                    _idx = (idx + bias) if bias_mode else idx
                    row, col = _idx // self.term_count, _idx % self.term_count

                    if len(table[row][col]) >= worker_per_term:
                        bias_mode = True
                        bias += 1
                    else:
                        table[row][col].append(worker_key.split("|")[0])
                        bias_mode = False
                        bias = 0
                        work_cnt += 1
                        idx += term

            return table, queue

    def non_assistant_scheduler(self, queue, days_cnt):
        _table, _queue = self.generate_work_table(
            queue=queue,
            table=[[0] * self.term_count for i in range(days_cnt)],
            days_cnt=days_cnt,
            worker_per_term=self.worker_per_term
        )

        return _table, _queue

    def assistant_scheduler(self, queue, days_cnt):
        table = [[0] * self.term_count for i in range(days_cnt)]

        senior = {}
        junior = {}

        for worker in queue:
            key = worker[0].split("|")[1]
            if key == "senior":
                senior[worker[0]] = worker[1]
            else:
                junior[worker[0]] = worker[1]

        senior_cnt, junior_cnt = 1, self.worker_per_term - 1

        _table_with_senior, _senior = self.generate_work_table(
            queue=senior,
            table=table,
            days_cnt=days_cnt,
            worker_per_term=senior_cnt
        )
        _table, _junior = self.generate_work_table(
            queue=junior_cnt,
            table=_table_with_senior,
            days_cnt=days_cnt,
            worker_per_term=junior_cnt
        )

        return _table, _senior, _junior

    def adjust_work_table(self):
        # TODO: 예외 관계 조정 & 중복 근무 수정 (금요일-토요일)
        pass

    @classmethod
    def week_table(cls):
        table = cls()
        return table
