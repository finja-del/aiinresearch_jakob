from fastapi import APIRouter, Query
from typing import Optional, List
from backend.services.ScopusService import ScopusService
from backend.services.OpenalexService import OpenAlexService
from backend.services.WosService import WOSService
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from backend.models.Ranking import Ranking
from backend.models.FilterCriteria import FilterCriteria, FilterCriteriaIn
import os


# 🔹 Define the router
router = APIRouter()

# 🔹 API route outside the class
@router.get("/search")
def search_route(
    q: str = Query(..., alias="q"),
    source: Optional[str] = Query(None),
    # language: Optional[str] = None,
    # author: Optional[str] = None,
    year_from: Optional[int] = Query(None, alias="year_from"),
    year_to: Optional[int] = Query(None, alias="year_to")
):
    if not q.strip():
        return []

    sources = [s.strip().lower() for s in (source or "").split(",")]
    filters = FilterCriteria(
        scopus="scopus" in sources,
        wos="web of science" in sources,
        openalex="openalex" in sources,
        # language=language,
        # author=author,
        start_year=year_from,
        end_year=year_to
    )

    controller = SearchController()
    results = controller.searchPapers(q, filters)
    return results

# 🔹 API route for POST requests
@router.post("/search")
def search_post(filters: FilterCriteriaIn):
    sources = [s.lower() for s in filters.source or []]

    filter_criteria = FilterCriteria(
        scopus="scopus" in sources,
        wos="web of web of science" in sources,
        openalex="openalex" in sources,
        # language=filters.language,
        # author=filters.author,
        start_year=filters.range.start if filters.range else None,
        end_year=filters.range.end if filters.range else None,
        ranking=filters.ranking,
        rating=filters.rating

    )

    controller = SearchController()
    return controller.searchPapers(filters.q, filter_criteria)

# 🔹 SearchController class
class SearchController:

    def __init__(self):
        base_path = os.path.dirname(__file__)  # ← liegt in controller/
        csv_path = os.path.join(base_path, '..', 'data', 'abc_ranking.csv')
        self.abc_ranking = Ranking(csv_path) #neu Finja

        # API-Clients initialisieren
        self.scopus = ScopusService(self.abc_ranking)
        self.openalex = OpenAlexService(self.abc_ranking)
        self.wos = WOSService(self.abc_ranking)

    def checkServices(self, filters):
        self.apiClients = []
        if filters.scopus:
            self.apiClients.append(self.scopus)
        if filters.openalex:
            self.apiClients.append(self.openalex)
        if filters.wos:
            self.apiClients.append(self.wos)

    def searchPapers(self, searchTerm: str, filters) -> list[dict]:
        self.checkServices(filters)
        all_results: list[PaperDTO] = []

        for apiClient in self.apiClients:
            source = apiClient.__class__.__name__.replace("Service", "")
            results = apiClient.getPaperList(searchTerm, filters)
            print(f"🔍 {source} found {len(results)} papers.")
            all_results += results

        return [paper.to_api_dict() for paper in all_results]
