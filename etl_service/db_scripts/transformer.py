import logging

from .models.film_work_model import FilmWorkModel

logger = logging.getLogger(__name__)


class Transformer:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def get_prepared_data(self):
        list_data = list(self.raw_data)
        if list_data:
            data_models = [FilmWorkModel(**item) for item in list_data]
            modified = list_data[-1].get('modified')
            logger.info(f"New modified: {modified}")
            return [{"_index": "movies", "_id": data.id, "_source": data.model_dump_json()} for data in
                    data_models], modified

        return [], None
