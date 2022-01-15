from dataclasses import dataclass, field

from domain.entity.user import User


@dataclass
class WorkMode(User):
    weekday: bool = field(default=True)
    holiday: bool = field(default=True)
