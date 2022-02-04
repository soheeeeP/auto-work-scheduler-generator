from dataclasses import dataclass, field


@dataclass
class User:
    id: int
    name: str
    rank: str
    status: str = field(default='Default')
    weekday_work_count: int = field(default=0)
    holiday_work_count: int = field(default=0)
    work_mode: str = field(default='on')
