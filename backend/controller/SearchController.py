import os #neu Finja
from services.ScopusService import ScopusService #neu Finja
from services.OpenalexService import OpenAlexService #neu Finja
from services.WosService import WOSService #neu Finja
from services.PaperRestService import PaperRestService #neu Finja

from models.PaperDTO import PaperDTO #neu Finja
from models.Ranking import Ranking #neu Finja


class SearchController:
    apiClients: list[PaperRestService]

    def __init__(self):

        base_path = os.path.dirname(__file__)  # ← liegt in controller/ #neu Finja
        csv_path = os.path.join(base_path, '..', 'data', 'abc_ranking.csv') #neu Finja
        self.abc_ranking = Ranking(csv_path) #neu Finja

        # self.config = config
        # self.journal_data = load_journal_ratings(config['rating_file'])

        # API-Clients initialisieren
        scopus = ScopusService(self.abc_ranking) #neu Finja
        openalex = OpenAlexService(self.abc_ranking) #neu Finja
        #TODO check API key wos = WOSService()

        self.apiClients = [scopus, openalex]

    def searchPapers(self, searchTerm: str) -> list[PaperDTO]:
        all_results: list[PaperDTO] = []

        for apiClient in self.apiClients:
            source_name = apiClient.__class__.__name__.replace("Service", "")
            results = apiClient.getPaperList(searchTerm)
            print(f"🔍 {source_name} found {len(results)} papers.")
            all_results += results

        return all_results

