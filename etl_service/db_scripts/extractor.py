from .db.postgres_extractor import PostgresExtractor
from .storage.storage import JsonFileStorage, State
from .transformer import Transformer


class Extractor:
    def __init__(self):
        self.postgres_extractor = PostgresExtractor()
        self.storage = State(JsonFileStorage("storage.json"))
        self.transformer = Transformer

    def extract(self):
        return self.postgres_extractor.extract_data(modified=self.storage.get_state("modified", '1970-01-01'))
