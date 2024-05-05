import pytest
from unittest.mock import Mock, patch
from google_workspace_posture.check import Check, CheckPriority, CheckStatus, CheckResult
from google_workspace_posture.services.admin_reports import AdminReports
from google_workspace_posture.services.admin_directory import AdminDirectory

from google_workspace_posture.checks.accounts import (
    require_2_step_verification_for_users,
    enforce_security_keys_for_admins
)

# Fixtures for enforce_security_keys_for_admins
@pytest.fixture
def security_keys_check_instance():
    return enforce_security_keys_for_admins()

@pytest.fixture
def security_keys_admin_reports_mock():
    with patch('google_workspace_posture.checks.accounts.AdminReports') as mock:
        yield mock

# Tests for enforce_security_keys_for_admins
def test_all_admins_have_keys(security_keys_check_instance, security_keys_admin_reports_mock):
    security_keys_admin_reports_mock.return_value.__enter__.return_value.load_data.return_value = [
        {'entity': {'userEmail': 'admin@example.com'}, 'parameters': [{'boolValue': 'true'}, {'boolValue': 'true'}, {'intValue': '1'}]}
    ]
    result = security_keys_check_instance.check()
    assert result.result == CheckStatus.PASS
    assert result.message == 'All admin users have security keys'

def test_some_admins_missing_keys(security_keys_check_instance, security_keys_admin_reports_mock):
    security_keys_admin_reports_mock.return_value.__enter__.return_value.load_data.return_value = [
        {'entity': {'userEmail': 'admin@example.com'}, 'parameters': [{'boolValue': 'true'}, {'boolValue': 'true'}, {'intValue': '0'}]},
        {'entity': {'userEmail': 'user@example.com'}, 'parameters': [{'boolValue': 'false'}, {'boolValue': 'false'}, {'intValue': '1'}]},
        {'entity': {'userEmail': 'admin2@example.com'}, 'parameters': [{'boolValue': 'true'}, {'boolValue': 'false'}, {'intValue': '0'}]}
    ]
    result = security_keys_check_instance.check()
    assert result.result == CheckStatus.FAIL
    assert 'admin@example.com' in result.message
    assert 'admin2@example.com' in result.message
    assert 'user@example.com' not in result.message

def test_no_data_security_keys(security_keys_check_instance, security_keys_admin_reports_mock):
    security_keys_admin_reports_mock.return_value.__enter__.return_value.load_data.return_value = []
    result = security_keys_check_instance.check()
    assert result.result == CheckStatus.PASS

# Fixtures for require_2_step_verification_for_users
@pytest.fixture
def two_step_verification_check_instance():
    return require_2_step_verification_for_users()

@pytest.fixture
def admin_directory_mock():
    with patch('google_workspace_posture.checks.accounts.AdminDirectory') as mock:
        yield mock

# Tests for require_2_step_verification_for_users
def test_not_enforced_but_enrolled(two_step_verification_check_instance, admin_directory_mock):
    admin_directory_mock.return_value.__enter__.return_value.load_data.return_value = [
        {'primaryEmail': 'user1@example.com', 'isEnrolledIn2Sv': True, 'isEnforcedIn2Sv': False},
        {'primaryEmail': 'user2@example.com', 'isEnrolledIn2Sv': True, 'isEnforcedIn2Sv': False}
    ]
    result = two_step_verification_check_instance.check()
    assert result.result == CheckStatus.PARTIAL_PASS
    assert 'user1@example.com' in result.message
    assert 'user2@example.com' in result.message

def test_not_enrolled(two_step_verification_check_instance, admin_directory_mock):
    admin_directory_mock.return_value.__enter__.return_value.load_data.return_value = [
        {'primaryEmail': 'user1@example.com', 'isEnrolledIn2Sv': False},
        {'primaryEmail': 'user2@example.com', 'isEnrolledIn2Sv': True, 'isEnforcedIn2Sv': True},
        {'primaryEmail': 'user3@example.com', 'isEnrolledIn2Sv': False}
    ]
    result = two_step_verification_check_instance.check()
    assert result.result == CheckStatus.FAIL
    assert 'user1@example.com' in result.message
    assert 'user3@example.com' in result.message

def test_all_users_enrolled(two_step_verification_check_instance, admin_directory_mock):
    admin_directory_mock.return_value.__enter__.return_value.load_data.return_value = [
        {'primaryEmail': 'user1@example.com', 'isEnrolledIn2Sv': True, 'isEnforcedIn2Sv': True},
        {'primaryEmail': 'user2@example.com', 'isEnrolledIn2Sv': True, 'isEnforcedIn2Sv': True}
    ]
    result = two_step_verification_check_instance.check()
    assert result.result == CheckStatus.PASS
    assert result.message == 'All users are enrolled in 2SV'


