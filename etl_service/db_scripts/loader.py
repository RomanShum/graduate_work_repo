import backoff
import os
from contextlib import closing

from elasticsearch import Elasticsearch, ConnectionError, TransportError
from elasticsearch.helpers import bulk

from .storage.storage import State, JsonFileStorage


class Loader:
    def __init__(self, data, modified):
        self.data = data
        self.modified = modified
        self.storage = State(JsonFileStorage("storage.json"))

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError), max_tries=5)
    def load(self):
        with closing(Elasticsearch(os.getenv('ELASTIC_PATH'))) as con:
            success, failed = bulk(con, self.data)
            self.storage.set_state(key="modified", value=self.modified.isoformat())
            return success, failed
