from dataclasses import dataclass, field


@dataclass
class WorkMode:
    weekday: bool = field(default=True)
    holiday: bool = field(default=True)
