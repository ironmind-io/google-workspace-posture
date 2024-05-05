from abc import ABC, abstractmethod
from enum import Enum
import pydantic

class Check(ABC):
    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
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
    PARTIAL_PASS = "partial_pass"
    FAIL = "fail"
    SKIPPED = "skipped"
    ERROR = "error"

class CheckMetadata(pydantic.BaseModel):
    id: str
    name: str
    description: str


class CheckResult(pydantic.BaseModel):
    id: str
    result: CheckStatus
    message: str

class CheckError(Exception):
    pass


