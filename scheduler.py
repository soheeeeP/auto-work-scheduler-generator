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
        setattr(self, 'organized_schedule', {})

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
            for user_id, value in queue.items():
                if value['status'] == '사수':
                    senior_queue[user_id] = value
                else:
                    junior_queue[user_id] = value
            for user_id, value in pre_queue.items():
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
                worker_per_term=self.worker_per_term
            )

        return True

    @staticmethod
    def calc_assigned_workers_cnt(table):
        x = 0
        for t in table:
            x += sum(len(_t) for _t in t)
        return x

    @staticmethod
    def find_table_idx_to_assign(table, term_count, worker_per_term, start_i):
        r, c = start_i // term_count, start_i % term_count
        for j in range(c, term_count):
            if len(table[r][j].keys()) < worker_per_term:
                return r * term_count + j

        for i in range(r + 1, len(table)):
            for j in range(0, term_count):
                if len(table[i][j].keys()) < worker_per_term:
                    return i * term_count + j

        return -1
        # return term_count * len(table)

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
        total_count = 0

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

            if diff > 0:
                sum_count += diff

            users_queue[user_id] = {
                "name": value["name"],
                "status": value["status"],
                "exp": on,
                "exp_terms_idx_list": exp_term_data if on else None,
                "work_count": max(diff, 0)
            }

            total_count += max(diff, 0)

        if total_count < needed_terms_in_week:
            up = max(needed_terms_in_week // len(users_queue), 1)
            for user_id, value in users_queue.items():
                users_queue[user_id]["work_count"] += up

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
        label = 'work_count'
        days_cnt = self.days_on_off.count(self.day_dict[day_key])

        work_table = getattr(self, 'table')
        organized_schedule = getattr(self, 'organized_schedule')

        work_queue = queue if isinstance(queue, dict) else dict(queue)
        pre_work_queue = pre_queue if isinstance(pre_queue, dict) else dict(pre_queue)

        pre_assigned_workers = self.calc_assigned_workers_cnt(work_table)

        needed_workers = days_cnt * self.term_count * worker_per_term
        if pre_assigned_workers > 0:
            needed_workers -= (days_cnt * self.term_count)

        while True:
            for worker_id, value in work_queue.items():
                assigned_workers_in_table = self.calc_assigned_workers_cnt(work_table) - pre_assigned_workers
                left_work_count_sum = sum(x[label] for x in work_queue.values())

                if assigned_workers_in_table == needed_workers or left_work_count_sum == 0:
                    setattr(self, 'table', work_table)
                    setattr(self, 'organized_schedule', organized_schedule)
                    return True

                work_term = max(2, needed_workers // left_work_count_sum)
                # 남아있는 work_count가 없으면, 편성할 수 없으므로 pass
                if value[label] == 0:
                    continue

                avg_work_count = max(needed_workers // len(work_queue), 1)
                cnt = value[label] if value[label] < avg_work_count else avg_work_count

                if worker_id in self.all_exp_relations_id_list:
                    special_relations, s_mode = set(self.all_exp_relations_id_list[worker_id]), True
                else:
                    special_relations, s_mode = None, False

                assigned_work_count = 0
                bias, bias_mode = 0, False
                idx = 0
                while assigned_work_count < cnt:
                    exps = value["exp_terms_idx_list"]
                    if exps and idx in exps:
                        bias_mode = True
                        x = exps.index(idx)
                        for i in range(x, len(exps) - 1):
                            if exps[i + 1] - exps[i] > 1:
                                bias = exps[i] - idx
                                break

                    start_i = (idx + bias) if bias_mode else idx
                    if start_i >= days_cnt * self.term_count:
                        bias, bias_mode = 0, False
                        break

                    _idx = self.find_table_idx_to_assign(work_table, self.term_count, worker_per_term, start_i)
                    if _idx == -1:
                        bias, bias_mode = 0, False
                        break

                    row, col = _idx // self.term_count, _idx % self.term_count

                    workers_set = set(work_table[row][col].keys())
                    if s_mode and workers_set.intersection(special_relations):
                        bias, bias_mode = 0, False
                        break

                    work_table[row][col][worker_id] = value["name"]
                    bias, bias_mode = 0, False
                    assigned_work_count += 1
                    idx = _idx + work_term

                    if worker_id in organized_schedule:
                        organized_schedule[worker_id] += 1
                    else:
                        organized_schedule[worker_id] = 1

                work_queue[worker_id][label] -= assigned_work_count

            work_queue = {k: v for k, v in sorted(work_queue.items(), key=lambda x: x[1][label], reverse=True)}

            left = needed_workers - self.calc_assigned_workers_cnt(work_table)
            up = max(math.ceil(left / len(work_queue)), 1)
            for user_id, val in work_queue.items():
                work_queue[user_id][label] += up

            work_queue = work_queue | pre_work_queue

    def adjust_work_table(self):
        pass

    @classmethod
    def init_scheduler(cls, base_date, days_on_off, day_key):
        scheduler = cls(base_date=base_date, days_on_off=days_on_off)
        scheduler(day_key)

        return getattr(scheduler, 'table'), getattr(scheduler, 'organized_schedule')
