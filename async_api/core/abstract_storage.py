import abc


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, index, id):
        """Получить данные по id"""

    @abc.abstractmethod
    def get_list(self, index, body):
        """Получить список."""
