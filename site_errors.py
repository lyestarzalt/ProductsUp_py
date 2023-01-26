# Author: Lyes Tarzalt
from dataclasses import dataclass



@dataclass
class SiteError:
    error_id: int
    pid: str
    error: int
    data: list
    site_id: int
    message: str
    links: list

