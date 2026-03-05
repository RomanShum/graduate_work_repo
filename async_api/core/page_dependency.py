from fastapi import Query
from core.settings import settings


class PageDependency:
    def __init__(self,
                 page_size: int = Query(title="page_size", description="Page size", ge=1, default=settings.page_size),
                 page_number: int = Query(title="page_number", description="Page number", ge=50,
                                          default=settings.page_number)):
        self.size = page_size
        self.number = page_number
