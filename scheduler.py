import math
from datetime import datetime
from itertools import combinations, product
from typing import Dict, List, Tuple, Set, Union

from db import database


class AdjustedWorkSchedulerGenerator:
    db = database

    day_dict = {
        "weekday": 1,
        "holiday": 0
    }

    def __init__(self, base_date: str, days_on_off: list):
        """
        :param base_date: schedule 생성 기준일 (%Y/%m/%d)
        :param days_on_off: 평일/휴일 설정값 list (평일 1, 휴일 0)

        :var self.term_count: 교대텀 설정값
        :var self.worker_per_term: 근무자 수
        :var self.assistant_mode: 사수/부사수 모드
        :var self.all_users: work_mode가 설정되어있는 전체 근무자 dict
        :var self.all_exp_relations: 예외 관계 dict
        :var self.all_exp_relations_id_list: 예외 관계정보(id값)가 저장된 undirected graph

        """
        self.base_date = base_date
        self.days_on_off = days_on_off

        config = self.db.config_repository.get_config()
        self.term_count, self.worker_per_term, self.assistant_mode = config

        self.all_users = self.db.work_mode_repository.get_work_mode_users()

        self.all_exp_relations = self.db.user_repository.get_all_exp_relation()
        self.all_exp_relations_id_list = {}
        for e in self.all_exp_relations:
            user_1_id, user_2_id = e['user_1_id'], e['user_2_id']
            if user_1_id not in self.all_exp_relations_id_list:
                self.all_exp_relations_id_list[user_1_id] = {user_2_id}
            else:
                self.all_exp_relations_id_list[user_1_id].add(user_2_id)

            if user_2_id not in self.all_exp_relations_id_list:
                self.all_exp_relations_id_list[user_2_id] = {user_1_id}
            else:
                self.all_exp_relations_id_list[user_2_id].add(user_1_id)

    def __call__(self, day_key):
        days_cnt = self.days_on_off.count(self.day_dict[day_key])
        setattr(self, 'table', [[{} for j in range(self.term_count)] for i in range(days_cnt)])
        setattr(self, 'assigned_worker_id_count', {})

        flag, q, pre_queue = self.workers_queue(day_key)
        if flag is False:
            return False

        setattr(self, 'queue', q)

        queue = getattr(self, 'queue')
        if self.worker_per_term == 1 or self.assistant_mode is False:
            self.generate_single_mode_worker_table(
                day_key=day_key,
                queue=queue,
                pre_queue=pre_queue,
                worker_per_term=self.worker_per_term
            )

        else:
            senior_queue, junior_queue = {}, {}
            pre_senior_queue, pre_junior_queue = {}, {}
            for user_id, value in queue:
                if value['status'] == '사수':
                    senior_queue[user_id] = value
                else:
                    junior_queue[user_id] = value
            for user_id, value in pre_queue:
                if value['status'] == '사수':
                    pre_senior_queue[user_id] = value
                else:
                    pre_junior_queue[user_id] = value

            self.generate_single_mode_worker_table(
                day_key=day_key,
                queue=senior_queue,
                pre_queue=pre_senior_queue,
                worker_per_term=1
            )
            self.generate_single_mode_worker_table(
                day_key=day_key,
                queue=junior_queue,
                pre_queue=pre_junior_queue,
                worker_per_term=self.worker_per_term - 1
            )

        return True

    @staticmethod
    def calc_assigned_workers_cnt(table):
        x = 0
        for t in table:
            x += sum(len(_t) for _t in t)
        return x

    def calc_exp_users_work_term(self, day_key, start_dt, end_dt):
        ymd_format, hm_format = '%Y/%m/%d', '%H:%M'

        if start_dt == '' or end_dt == '':
            return False, None

        term = 24 // self.term_count
        _base_date = datetime.strptime(self.base_date, ymd_format)

        _start = start_dt.split(' ')
        _end = end_dt.split(' ')

        s_date = datetime.strptime(_start[0], ymd_format)
        e_date = datetime.strptime(_end[0], ymd_format)

        if e_date < _base_date or (s_date - _base_date).days >= len(self.days_on_off):
            return False, None

        s_time_h = datetime.strptime(_start[1], hm_format).hour
        e_time_h = datetime.strptime(_end[1], hm_format).hour

        s_row, s_col = (s_date - _base_date).days, s_time_h // term
        e_row = (e_date - _base_date).days if (e_date - _base_date).days < len(self.days_on_off) else len(
            self.days_on_off) - 1
        e_col = e_time_h // term

        exp = []  # 근무를 제해야 하는 term의 번호가 담긴 list
        for i in range(s_row * self.term_count + s_col, e_row * self.term_count + e_col + 1):
            r_i, c_i = i // self.term_count, i % self.term_count
            if self.days_on_off[r_i] == self.day_dict[day_key]:
                exp.append(i)

        return True, exp

    def workers_queue(self, day_key) -> Tuple[bool, Union[Dict, None], Union[Dict, None]]:
        sum_count = 0
        max_work_count = self.db.user_repository.get_max_work_count()[day_key]

        days_cnt = self.days_on_off.count(self.day_dict[day_key])
        if days_cnt == 0:
            return False, None, None

        needed_terms_in_week = self.term_count * self.days_on_off.count(self.day_dict[day_key])

        users_queue = {}
        for user_id, value in self.all_users.items():
            on, exp_term_data = self.calc_exp_users_work_term(
                day_key=day_key,
                start_dt=value['exp_start_datetime'],
                end_dt=value['exp_end_datetime']
            )
            work_count = value[f'{day_key}_work_count']

            diff = max_work_count - work_count
            if on:
                ratio = (needed_terms_in_week - len(exp_term_data)) / needed_terms_in_week
                diff = math.floor(diff * ratio)

            if diff <= 0:
                continue

            sum_count += diff
            users_queue[user_id] = {
                "name": value["name"],
                "status": value["status"],
                "exp": on,
                "exp_terms_idx_list": exp_term_data if on else None,
                "work_count": diff
            }

        avg_count = sum_count // len(users_queue)

        workers, pre_workers = {}, {}
        for user_id, value in users_queue.items():
            if avg_count <= value["work_count"]:
                workers[user_id] = value
            else:
                pre_workers[user_id] = value

        workers_queue = {k: v for k, v in sorted(workers.items(), key=lambda x: x[1]["work_count"], reverse=True)}
        pre_workers_queue = {k: v for k, v in
                             sorted(pre_workers.items(), key=lambda x: x[1]["work_count"], reverse=True)}

        return True, workers_queue, pre_workers_queue

    def generate_worker_group(self, single_group, sub_group, worker_per_term) -> Set:
        sub_group, sub_ids_list = [], list(sub_group.keys())

        for u_id in sub_ids_list:
            left = set(sub_ids_list)
            if u_id in self.all_exp_relations_id_list:
                left = left.difference(set(self.all_exp_relations_id_list[u_id]))

            sub_group.extend(list(combinations(left, worker_per_term)))

        if single_group is None:
            return set(sub_group)

        single_ids_list = list(single_group.keys())

        group = []
        for elem in product(single_ids_list, sub_group):
            if elem[0] in self.all_exp_relations_id_list and set(elem[1]).intersection(
                    self.all_exp_relations_id_list[elem[0]]):
                continue
            group.extend((elem[0], *elem[1]))

        return set(group)

    def generate_single_mode_worker_table(self, day_key, queue, pre_queue, worker_per_term):
        days_cnt = self.days_on_off.count(self.day_dict[day_key])
        needed_workers_in_week = days_cnt * (self.term_count * worker_per_term)

        work_table = getattr(self, 'table')
        assigned_worker_id_count = getattr(self, 'assigned_worker_id_count')

        work_queue = queue if isinstance(queue, dict) else dict(queue)
        pre_work_queue = pre_queue if isinstance(pre_queue, dict) else dict(pre_queue)

        avg_work_count = needed_workers_in_week / len(work_queue)

        label = 'work_count'
        while True:
            for worker_id, value in work_queue.items():
                assigned_workers = self.calc_assigned_workers_cnt(work_table)
                all_workers_work_count_sum = sum(x[label] for k, x in work_queue.items())
                if assigned_workers == needed_workers_in_week:
                    setattr(self, 'table', work_table)
                    setattr(self, 'assigned_worker_id_count', assigned_worker_id_count)
                    return True

                if value[label] == 0:
                    continue

                cnt = value[label] if value[label] < avg_work_count else avg_work_count

                term = max(2, needed_workers_in_week // all_workers_work_count_sum)
                assigned_work_cnt, idx, bias, bias_mode = 0, 0, 0, False
                if worker_id in self.all_exp_relations_id_list:
                    exp_users, exp_mode = set(self.all_exp_relations_id_list[worker_id]), True
                else:
                    exp_users, exp_mode = None, False

                while idx < days_cnt * self.term_count and assigned_work_cnt < cnt:
                    _idx = (idx + bias) if bias_mode else idx
                    if value['exp_terms_idx_list'] and _idx in value['exp_terms_idx_list']:
                        bias, bias_mode = bias + 1, True
                        continue

                    row, col = _idx // self.term_count, _idx % self.term_count

                    if row >= days_cnt or col >= self.term_count:
                        idx = 0
                        bias, bias_mode = 0, False
                        continue

                    workers_set = set(work_table[row][col].keys())
                    if len(workers_set) >= self.worker_per_term or (exp_mode and workers_set.intersection(exp_users)):
                        idx += 1
                        continue

                    work_table[row][col][worker_id] = value['name']
                    bias, bias_mode = 0, False
                    assigned_work_cnt += 1
                    idx = _idx + term

                    if worker_id in assigned_worker_id_count:
                        assigned_worker_id_count[worker_id] += 1
                    else:
                        assigned_worker_id_count[worker_id] = 1

                work_queue[worker_id][label] -= assigned_work_cnt

            left = needed_workers_in_week - self.calc_assigned_workers_cnt(work_table)
            if sum(v[label] for v in work_queue.values()) == 0:
                up_1 = math.ceil(left / len(work_queue))
                for user_id, val in work_queue.items():
                    work_queue[user_id][label] += up_1

            work_queue = pre_work_queue | work_queue

    def adjust_work_table(self):
        pass

    @classmethod
    def init_scheduler(cls, base_date, days_on_off, day_key):
        scheduler = cls(base_date=base_date, days_on_off=days_on_off)
        scheduler(day_key)

        return getattr(scheduler, 'table'), getattr(scheduler, 'assigned_worker_id_count')
