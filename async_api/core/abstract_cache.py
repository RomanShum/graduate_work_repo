import abc

from models.film import ResponseFilm, ResponseFilmList


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    def set_data(self, key, data) -> None:
        """Сохранить данные в хранилище."""

    @abc.abstractmethod
    def get_data(self, key) -> ResponseFilm | ResponseFilmList | None:
        """Получить данные из хранилища."""
