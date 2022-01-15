from datetime import date, time
from dataclasses import dataclass, field


@dataclass
class Schedule:
    date: date
    day: str            # weekday, holiday

    term_idx: int       # term_idx (1~24)
    start_time: time    # start_time: (24 / config.term_count) * (term_idx - 1)
    end_time: time      # end_time: (24 / config.term_count) * term_idx

    worker_id: int
