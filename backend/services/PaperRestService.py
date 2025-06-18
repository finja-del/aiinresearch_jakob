from abc import ABC, abstractmethod
from datetime import date
from models.PaperDTO import PaperDTO

class PaperRestService(ABC):

    @abstractmethod
    def getPaperList(self, searchTerm: str) -> list[PaperDTO]:
        return []

    #TODO:  beforeDate: date, afterDate: date nacher in Funktionsparameter einfügen