import sys
import logging
import time

import backoff

from db_scripts.extractor import Extractor
from db_scripts.transformer import Transformer
from db_scripts.loader import Loader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def backoff_handler(details):
    print(f"Delay {details['wait']:.1f} seconds after {details['tries']} tries")


@backoff.on_exception(backoff.expo, Exception, max_tries=5, on_backoff=backoff_handler)
def run():
    raw_data = Extractor().extract()
    prepared_data, modified = Transformer(raw_data).get_prepared_data()
    if prepared_data:
        success, failed = Loader(prepared_data, modified).load()
        logger.info(f"Успешные записи: {success}")
        logger.info(f"Записи с ошибками: {failed}")
    else:
        logger.info(f"Данных для записи нет")


def app():
    logger.info("Start")
    while True:
        try:
            run()
        except Exception as e:
            raise e
        finally:
            time.sleep(10)


if __name__ == "__main__":
    app()
