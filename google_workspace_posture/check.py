from abc import ABC, abstractmethod
from enum import Enum
import pydantic

class Check(ABC):
    
    @property
    @abstractmethod
    def check_id(self):
        pass

    @property
    @abstractmethod
    def check_priority(self):
        pass
    
    @property
    @abstractmethod
    def check_name(self):
        pass

    @property
    @abstractmethod
    def check_description(self):
        pass

    @abstractmethod
    def check(self):
        pass

class CheckPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"

class CheckMetadata(pydantic.BaseModel):
    check_id: str
    check_name: str
    check_description: str


class CheckResult(pydantic.BaseModel):
    check_id: str
    check_result: CheckStatus
    check_message: str



