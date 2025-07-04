from datetime import date
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel


# 🔹 Intern genutzte Klasse (Logik, nicht direkt API-Eingabe)
@dataclass
class FilterCriteria:

    def __init__(
        self,
        scopus: bool = True,
        wos: bool = False,
        openalex: bool = False,
        #language: Optional[List[str]] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        ranking: Optional[List[str]] = None,
        rating: Optional[List[str]] = None,
        author: Optional[List[str]] = None,
        #author: Optional[List[str]] = None
    ):
        self.scopus = scopus
        self.wos = wos
        self.openalex = openalex
        #self.language = language or []
        self.start_year = start_year
        self.end_year = end_year
        self.ranking = ranking or []
        self.rating = rating or []
        self.author = author or []
        #self.author = author or []

    @property
    def start_date(self) -> Optional[date]:
        return date(self.start_year, 1, 1) if self.start_year else None

    @property
    def end_date(self) -> Optional[date]:
        return date(self.end_year, 12, 31) if self.end_year else None


# 🔹 POST-Request-Modell für FastAPI – direkt aus JSON befüllbar
class YearRange(BaseModel):
    start: Optional[int]
    end: Optional[int]

class FilterCriteriaIn(BaseModel):
    q: str
    range: Optional[YearRange]
    ranking: Optional[List[str]] = []  # z. B. ["VHB", "ABDC"]
    rating: Optional[List[str]] = []   # z. B. ["A*", "A", "B"]
    source: Optional[List[str]] = []   # z. B. ["scopus", "wos"]
    #language: Optional[List[str]] = [] # z. B. ["en", "de"]
    #author: Optional[List[str]] = []  # z. B. ["Mustermann, Max", "Müller, Anna"]
