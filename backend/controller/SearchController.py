from fastapi import APIRouter, Query
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.services.Deduplication.DuplicateMergeService import DuplicateMergeService
from backend.services.Filterservices.AbdcService import AbdcService
from backend.services.ApiServices.ScopusService import ScopusService
from backend.services.ApiServices.OpenAlexService import OpenAlexService
from backend.services.Filterservices.VhbService import VhbService
from backend.services.ApiServices.WosService import WOSService
from backend.models.PaperDTO import PaperDTO
from backend.models.FilterCriteria import FilterCriteria, FilterCriteriaIn


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
        wos="web of science" in sources,
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

        # VHB-Ranking initialisieren
        self.vhbRanking = VhbService()
        self.abdcRanking = AbdcService()

        # API-Clients initialisieren
        self.scopus = ScopusService(self.vhbRanking, self.abdcRanking)
        self.openalex = OpenAlexService(self.vhbRanking, self.abdcRanking)
        self.wos = WOSService(self.vhbRanking, self.abdcRanking)

    def checkServices(self, filters):
        self.apiClients = []
        if filters.scopus:
            print("🔍 Scopus is enabled.")
            self.apiClients.append(self.scopus)
        if filters.openalex:
            print("🔍 OpenAlex is enabled.")
            self.apiClients.append(self.openalex)
        if filters.wos:
            print("🔍 Web of Science is enabled.")
            self.apiClients.append(self.wos)

    def searchPapers(self, searchTerm: str, filters) -> list[dict]:
        """
        Executes enabled data‑source queries in parallel using a ThreadPool.
        Falls back to sequential execution if only one source is active.
        """
        self.checkServices(filters)
        all_results: list[PaperDTO] = []

        if len(self.apiClients) <= 1:
            # ╰─► sequential fallback (existing behaviour)
            for apiClient in self.apiClients:
                source = apiClient.__class__.__name__.replace("Service", "")
                results = apiClient.getPaperList(searchTerm, filters)
                for paper in results:
                    # set primary source name
                    paper.source = source
                    # keep sources set and count in sync (PaperDTO merge‑ready)
                    if hasattr(paper, "sources"):
                        paper.sources.add(source)
                        paper.sourceCount = len(paper.sources)
                print(f"🔍 {source} found {len(results)} papers.")
                all_results += results
        else:
            # ╰─► parallel execution
            with ThreadPoolExecutor(max_workers=len(self.apiClients)) as executor:
                future_map = {
                    executor.submit(c.getPaperList, searchTerm, filters): c
                    for c in self.apiClients
                }
                for future in as_completed(future_map):
                    apiClient = future_map[future]
                    source = apiClient.__class__.__name__.replace("Service", "")
                    try:
                        results = future.result()
                    except Exception as exc:
                        print(f"[ERR] {source} raised {exc!r}")
                        results = []
                    for paper in results:
                        # set primary source name
                        paper.source = source
                        # keep sources set and count in sync (PaperDTO merge‑ready)
                        if hasattr(paper, "sources"):
                            paper.sources.add(source)
                            paper.sourceCount = len(paper.sources)
                    print(f"🔍 {source} found {len(results)} papers.")
                    all_results += results

        return DuplicateMergeService.merge_duplicates(all_results)
