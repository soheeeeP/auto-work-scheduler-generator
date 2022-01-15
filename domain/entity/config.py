from dataclasses import dataclass, field


@dataclass
class Config:
    term_count: int = field(default=3)
    worker_per_term: int = field(default=1)
    assistant_mode: bool = field(default=False)
