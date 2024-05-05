import pytest
from pydantic import ValidationError

from google_workspace_posture.check import Check, CheckPriority, \
        CheckStatus, CheckMetadata, CheckResult

# Implementing a concrete class for testing
class ConcreteCheck(Check):
    def __init__(self, id, priority, name, description):
        self._check_id = id
        self._priority = priority
        self._name = name
        self._description = description

    @property
    def id(self):
        return self._check_id

    @property
    def priority(self):
        return self._priority

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def check(self):
        return CheckResult(id=self.id, result=CheckStatus.PASS, message="OK")


# Testing Pydantic models
def test_check_metadata_model():
    metadata = CheckMetadata(id="001", name="Basic Check", description="A basic operational check.")
    assert metadata.id == "001"
    assert metadata.name == "Basic Check"
    assert metadata.description == "A basic operational check."

def test_check_result_model():
    result = CheckResult(id="001", result=CheckStatus.PASS, message="All good.")
    assert result.id == "001"
    assert result.result == CheckStatus.PASS
    assert result.message == "All good."

def test_invalid_check_result():
    with pytest.raises(ValidationError):
        CheckResult(id="002", result="unknown_status", message="This should fail.")

# Testing the abstract methods implementation
def test_concrete_check():
    check = ConcreteCheck("001", CheckPriority.LOW, "Test Check", "Testing the abstract methods.")
    assert check.id == "001"
    assert check.priority == CheckPriority.LOW
    assert check.name == "Test Check"
    assert check.description == "Testing the abstract methods."
    result = check.check()
    assert result.id == "001"
    assert result.result == CheckStatus.PASS
    assert result.message == "OK"



