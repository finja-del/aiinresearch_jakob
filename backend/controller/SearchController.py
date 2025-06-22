from backend.services.ScopusService import ScopusService
from backend.services.OpenalexService import OpenAlexService
from backend.services.WosService import WOSService
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from backend.models.Ranking import Ranking
import os
from flask import Blueprint, request, jsonify

# 🔹 Define the blueprint
search_blueprint = Blueprint("search_api", __name__)

# 🔹 API route outside the class
@search_blueprint.route("/api/search", methods=["GET"])
def search_route():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    controller = SearchController()
    results = controller.searchPapers(query)
    return jsonify(results)


# 🔹 SearchController class
class SearchController:
    apiClients: list[PaperRestService]

    def __init__(self):
        base_path = os.path.dirname(__file__)
        csv_path = os.path.join(base_path, '..', 'data', 'abc_ranking.csv')
        self.abc_ranking = Ranking(csv_path)

        scopus = ScopusService(self.abc_ranking)
        openalex = OpenAlexService(self.abc_ranking)
        # TODO: Add WOSService when ready

        self.apiClients = [scopus, openalex]

    def searchPapers(self, searchTerm: str) -> list[dict]:
        all_results: list[PaperDTO] = []

        for apiClient in self.apiClients:
            source_name = apiClient.__class__.__name__.replace("Service", "")
            results = apiClient.getPaperList(searchTerm)
            print(f"🔍 {source_name} found {len(results)} papers.")
            all_results += results

        return [paper.to_api_dict() for paper in all_results]
