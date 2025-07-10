# services/wos_service.py
# Web of Science API-Anbindung (nur wenn API-Zugang vorhanden)
from typing import Optional

import requests
import os
from backend.models.FilterCriteria import FilterCriteria
from backend.services.ApiServices.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from dotenv import load_dotenv


class WOSService(PaperRestService):
    def __init__(self, VhbRanking, abdcRanking):
        load_dotenv()
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        self.vhbRanking = VhbRanking
        self.abdcRanking = abdcRanking


    def query(self, search_term: str, filter_criteria: Optional[FilterCriteria] = None) -> list[PaperDTO]:
        headers = {'X-ApiKey': self.api_key, 'Accept': 'application/json'}
        params = {
            'db': 'WOK',
            'q': self.filterService(search_term, filter_criteria),
            'limit': 20
        }

        results: list[PaperDTO] = []

        try:
            response = requests.get(self.base_url, headers=headers, params=params)

            response.raise_for_status()
            data = response.json()

            #print(json.dumps(data, indent=2))

            hits = data.get("hits", [])
            authors = []
            citations = 0
            for hit in hits:
                title = hit.get('title') or 'N/A'
                if isinstance(title, dict):
                    title = title.get('value', 'N/A')

                doi = hit.get('identifiers', {}).get('doi')
                author_objs = hit.get('names', {}).get('authors') or []
                authors = [a.get('displayName', 'N/A') for a in author_objs]
                citations = hit.get("citations", [{}])[0].get('count', 0)
                journal = hit.get('source', {}).get('sourceTitle')
                year = hit.get('source', {}).get('publishYear')
                eissn = hit.get('identifiers', {}).get('eissn')
                issn = hit.get('identifiers', {}).get('issn')
                abstract = hit.get('description', '') or 'N/A'
                url = f"https://doi.org/{doi}" if doi else None

                paper = PaperDTO(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    date=str(year) if year else "1900",
                    source='WOK',
                    vhbRanking=self.vhbRanking.getRanking(journal, issn),
                    abdcRanking= self.abdcRanking.getRanking(journal, issn),
                    journal_name=journal,
                    issn=issn,
                    eissn=eissn,
                    doi=doi,
                    url=url,
                    citations=citations
                )

                print(f"[DEBUG] Paper: {paper.title} | Journal: {paper.journal_name} | ISSN: {issn} | VHB-Ranking: {paper.vhbRanking}")
                results.append(paper)

        except requests.exceptions.RequestException as e:
          print(f"[WOS API Fehler]: {e}")

        return results




    def filterService(self, search_term: str, filter_criteria: Optional[FilterCriteria] = None) -> str:
        q = f"TI={search_term}"
        print(f"Fliter start data:  {filter_criteria.start_year}")
        if filter_criteria.start_year and filter_criteria.end_year:
            q += f" AND DOP={filter_criteria.start_year}/{filter_criteria.end_year}"
        elif filter_criteria.start_year and not filter_criteria.end_year:
            q += f" AND DOP={filter_criteria.start_year}"
        elif filter_criteria.end_year and not filter_criteria.start_year:
            q += f" AND DOP={filter_criteria.end_year}"
        if filter_criteria.author:
            q += f" AND AU={filter_criteria.author}"

        print(q)
        return q


    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return self.query(searchTerm, filters)



