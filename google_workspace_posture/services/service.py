from abc import ABC, abstractmethod

class Service(ABC):
    
    @abstractmethod
    def validate_config(self):
        '''
        Checks whether the correct config is provided
        Returns empty string if config is valid
        Returns error message if config is invalid
        '''
        pass

    def load_service(self):
        '''
        Loads the service
        '''
        pass
