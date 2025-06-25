from typing import Optional
from datetime import date

class FilterCriteria:
    def __init__(
        self,
        scopus: bool = True,
        wos: bool = False,
        openalex: bool = False,
        language: Optional[str] = None,
        author: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ):
        self.scopus = scopus
        self.wos = wos
        self.openalex = openalex
        self.language = language
        self.author = author
        self.start_year = start_year
        self.end_year = end_year

    @property
    def start_date(self) -> Optional[date]:
        return date(self.start_year, 1, 1) if self.start_year else None

    @property
    def end_date(self) -> Optional[date]:
        return date(self.end_year, 12, 31) if self.end_year else None

