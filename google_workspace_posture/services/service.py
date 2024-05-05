from abc import ABC, abstractmethod


class ServiceError(Exception):
    pass

class Service(ABC):
    '''
    Abstract class for services
    Generally to be used in the following manner:
    with Service(config) as service:
        data = service.load_data(any, user, params)
        my_check(data)
    '''

    @abstractmethod
    def setup(self):
        '''
        Loads the service from any configuration.
        '''
        pass

    @abstractmethod
    def load_data(self):
        '''
        Loads data from the service
        '''
        pass

    def teardown(self):
        '''
        Unloads the service
        '''
        pass


    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()
        return False
