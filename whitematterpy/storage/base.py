from abc import ABC, abstractmethod

class StorageBase(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def put(self, key, value):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    @abstractmethod
    def iterator(self):
        pass

    @abstractmethod
    def write_batch(self, operations):
        pass

    @abstractmethod
    def create_column_family(self, name):
        pass

    @abstractmethod
    def drop_column_family(self, name):
        pass

    @abstractmethod
    def list_column_families(self):
        pass

    @abstractmethod
    def get_cf(self, cf_name, key):
        pass

    @abstractmethod
    def put_cf(self, cf_name, key, value):
        pass

    @abstractmethod
    def delete_cf(self, cf_name, key):
        pass

    @abstractmethod
    def compact_range(self, begin, end):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def close(self):
        pass