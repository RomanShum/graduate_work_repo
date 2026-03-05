from contextlib import closing
import logging

import psycopg
from psycopg.rows import dict_row

from .settings import Settings

logger = logging.getLogger(__name__)
BATCH = 100


class PostgresExtractor:
    def __init__(self):
        settings = Settings()

        self.dsl = {
            'dbname': settings.postgres_db,
            'user': settings.postgres_user,
            'password': settings.postgres_password,
            'host': settings.sql_host,
            'port': settings.sql_port
        }

    def extract_data(self, modified):
        logger.info(f"modified: {modified}")
        with closing(psycopg.connect(**self.dsl,
                                     row_factory=dict_row)) as conn:
            with closing(conn.cursor(row_factory=dict_row)) as cur:
                cur.execute(self.get_query(), {'modified': modified})
                logger.info(f"Найдено строк: {cur.rowcount}")
                while True:
                    batch = cur.fetchmany(BATCH)
                    if not batch:
                        break
                    yield from batch

    def get_query(self):
        return """WITH film_modified as (SELECT fw.id,
                            GREATEST(
                                MAX(fw.modified),
                                MAX(g.modified),
                                MAX(p.modified)) AS max_modified
                    FROM content.film_work fw
                    LEFT JOIN content.genre_film_work gfw ON
                        gfw.film_work_id = fw.id
                    LEFT JOIN content.genre g ON
                        g.id = gfw.genre_id
                    LEFT JOIN content.person_film_work pfw ON
                        pfw.film_work_id = fw.id
                    LEFT JOIN content.person p ON
                        p.id = pfw.person_id
                    GROUP BY fw.id
                 )
            SELECT fw.id,
                    fw.title,
                    fw.description, fw.rating as imdb_rating,
                    fm.max_modified as modified,
                    array_agg(distinct g.name) as genres,
                    coalesce(json_agg(distinct jsonb_build_object('id', p.id, 'name',p.full_name)) filter (where pfw.role='actor'), '[]') as actors,
                    coalesce(json_agg(distinct jsonb_build_object('id', p.id, 'name',p.full_name)) filter (where pfw.role='writer'), '[]') as writers,
                    coalesce(json_agg(distinct jsonb_build_object('id', p.id, 'name',p.full_name)) filter (where pfw.role='director'), '[]') as directors,
                    coalesce(json_agg(distinct p.full_name) filter (where pfw.role='actor'), '[]') as actors_names,
                    coalesce(json_agg(distinct p.full_name) filter (where pfw.role='writer'), '[]') as writers_names,
                    coalesce(json_agg(distinct p.full_name) filter (where pfw.role='director'), '[]') as director_names
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw on fw.id = gfw.film_work_id
            LEFT JOIN content.genre g on gfw.genre_id =g.id
            LEFT JOIN content.person_film_work pfw on fw.id = pfw.film_work_id 
            LEFT JOIN content.person p on p.id = pfw.person_id
            JOIN film_modified fm on fw.id = fm.id
            WHERE fm.max_modified > %(modified)s
            GROUP BY fw.id, fm.max_modified
            ORDER BY fm.max_modified
            """
