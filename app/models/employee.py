from dataclasses import dataclass

@dataclass
class Employee:
    id: int
    first_name: str
    last_name: str
    contact_info: str
    department: str
    position: str
    location: str
    status: str
    organization_id: int