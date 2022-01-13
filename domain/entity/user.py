from dataclasses import dataclass, field


@dataclass
class User:
    id: int
    name: str
    rank: str
    status: str = field(default='Default')
