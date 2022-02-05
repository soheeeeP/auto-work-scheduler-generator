import operator

from main import database


class WorkSchedulerGenerator:
    db = database

    def __init__(self):
        self.term_count, self.worker_per_term, self.assistant_mode = self.db.config_repository.get_config()

        self.weekday_workers = "weekday"
        self.holiday_workers = "holiday"

        if self.assistant_mode:
            self.weekday_T, w_seniorLeft, w_juniorLeft = self.assistant_scheduler(
                                                            queue=self.weekday_workers['queue'],
                                                            days_cnt=5)
            w_workersLeft = [w_seniorLeft, w_juniorLeft]

            self.holiday_T, h_seniorLeft, h_juniorLeft = self.assistant_scheduler(
                                                            queue=self.holiday_workers['queue'],
                                                            days_cnt=2)
            h_workersLeft = [h_seniorLeft, h_juniorLeft]
        else:
            self.weekday_T, w_workersLeft = self.non_assistant_scheduler(
                                                queue=self.weekday_workers['queue'],
                                                days_cnt=5)
            self.holiday_T, h_workersLeft = self.non_assistant_scheduler(
                                                queue=self.holiday_workers['queue'],
                                                days_cnt=2)

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

    @staticmethod
    def calc_assigned_workers_cnt(table):   # TODO: time complexity 개선하기
        x = 0
        for t in table:
            x += sum(len(_t) for _t in t)
        return x

    def get_workers(self, day):
        sum_count = 0
        max_work_count = self.db.user_repository.get_max_work_count()[day]
        key = "weekday" if day == "weekday" else "holiday"

        users = self.db.user_repository.get_work_mode_users()

        users_work_count = {}
        for u in users:
            label = f"{u['id']}|{u['status'].lower()}"
            diff = max_work_count - u[f'{key}_work_count']
            if diff > 0:
                sum_count += diff
                users_work_count[label] = diff

        avg_count = sum_count // len(users_work_count)

        workers = {}
        pre_workers = {}
        for k, v in users_work_count.items():
            if avg_count <= v:
                workers[k] = v
            else:
                pre_workers[k] = v

        workers_queue = {
            "queue": sorted(workers.items(), key=operator.itemgetter(1), reverse=True),
            "pre_queue": sorted(pre_workers.items(), key=operator.itemgetter(1), reverse=True)
        }

        return workers_queue

    def generate_work_table(self, queue, table, days_cnt, worker_per_term):
        _table = table.copy()

        _queue = queue if isinstance(queue, dict) else dict(queue)

        total_needed_workers = (days_cnt * self.term_count) * worker_per_term
        avg_count = total_needed_workers // len(_queue)

        while True:
            for key, value in _queue.items():
                if self.calc_assigned_workers_cnt(_table) == total_needed_workers or sum(_queue.values()) == 0:
                    return _table, _queue

                if value == 0:
                    continue

                if value < avg_count:
                    cnt = value
                else:
                    cnt = avg_count

                term = total_needed_workers // cnt
                work_cnt = 0
                idx = 0
                bias, bias_mode = 0, False

                while idx < days_cnt * self.term_count:
                    if work_cnt == cnt:
                        break

                    _idx = (idx + bias) if bias_mode else idx
                    row, col = _idx // self.term_count, _idx % self.term_count

                    if len(_table[row][col]) >= worker_per_term:
                        bias_mode = True
                        bias += 1
                    else:
                        _table[row][col].append(int(key.split("|")[0]))
                        bias_mode = False
                        bias = 0
                        work_cnt += 1
                        idx = _idx + term

                _queue[key] -= work_cnt

    def non_assistant_scheduler(self, queue, days_cnt):
        return self.generate_work_table(
            queue=queue,
            table=[[[] for j in range(self.term_count)] for i in range(days_cnt)],
            days_cnt=days_cnt,
            worker_per_term=self.worker_per_term
        )

    def assistant_scheduler(self, queue, days_cnt):
        table = [[[] for j in range(self.term_count)] for i in range(days_cnt)]

        senior = {}
        junior = {}

        for worker in queue:
            key = worker[0].split("|")[1]
            if key == "사수":
                senior[worker[0]] = worker[1]
            else:
                junior[worker[0]] = worker[1]

        senior_cnt, junior_cnt = 1, self.worker_per_term - 1

        _senior_assigned_table, _senior_left = self.generate_work_table(
            queue=senior,
            table=table,
            days_cnt=days_cnt,
            worker_per_term=senior_cnt
        )

        _table, _junior_left = self.generate_work_table(
            queue=junior,
            table=_senior_assigned_table,
            days_cnt=days_cnt,
            worker_per_term=junior_cnt
        )

        return _table, _senior_left, _junior_left

    def adjust_work_table(self):
        # TODO: 예외 관계 조정 & 중복 근무 수정 (금요일-토요일)
        pass

    @classmethod
    def week_table(cls):
        table = cls()
        return table
