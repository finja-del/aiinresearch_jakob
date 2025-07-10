from abc import ABC, abstractmethod
from datetime import date
from backend.models.PaperDTO import PaperDTO
from backend.models.FilterCriteria import FilterCriteria

class PaperRestService(ABC):

    @abstractmethod
    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return []

