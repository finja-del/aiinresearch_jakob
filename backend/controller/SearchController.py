import os #neu Finja
#from distutils.command.check import check
from typing import List

from backend.models.FilterCriteria import FilterCriteria
from backend.services.ScopusService import ScopusService
from backend.services.OpenalexService import OpenAlexService
from backend.services.WosService import WOSService
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from backend.models.Ranking import Ranking


class SearchController:

    def __init__(self):

        self.apiClients = []

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

    def searchPapers(self, searchTerm, filters):
        self.checkServices(filters)
        all_results = []
        for apiClient in self.apiClients:
            all_results += apiClient.getPaperList(searchTerm, filters)
        return all_results
