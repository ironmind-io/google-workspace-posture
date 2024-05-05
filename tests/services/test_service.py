import pytest
from unittest.mock import Mock, patch

from google_workspace_posture.services.service import Service, ServiceError

class ConcreteService(Service):

    def __init__(self, config):
        self.config = config

    def validate_config(self):
        if not hasattr(self, 'config') or not self.config.get('valid', False):
            return "Configuration is invalid"
        return ""

    def setup(self):
        # Setup logic here, potentially setting up resources
        self.resource = "Resource is setup"

    def load_data(self):
        return "data loaded"

    def teardown(self):
        # Cleanup resources here
        pass

@pytest.fixture
def service():
    # Setting up a service instance with configuration
    return ConcreteService(config={'valid': True})

def test_service_context_manager_pass(service):
    # Test that entering the context with a valid config works as expected
    with service as s:
        assert s.resource == "Resource is setup"

def test_service_teardown_called():
    # Test that teardown is called after exiting the context
    with patch.object(ConcreteService, 'teardown') as mock_teardown:
        with ConcreteService(config={'valid': True}) as service:
            pass
    mock_teardown.assert_called_once()

def test_service_exception_handling():
    # Test the service correctly handles exceptions within the context
    with patch.object(ConcreteService, 'load_data', side_effect=Exception("Test exception")):
        with pytest.raises(Exception) as excinfo:
            with ConcreteService(config={'valid': True}) as service:
                service.load_data()
    assert str(excinfo.value) == "Test exception"
    # No explicit assert for teardown as it should be called regardless of the exception



