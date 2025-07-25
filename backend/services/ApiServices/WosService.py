# services/wos_service.py
# Web of Science API-Anbindung (nur wenn API-Zugang vorhanden)
from typing import Optional

import requests
import os
from backend.models.FilterCriteria import FilterCriteria
from backend.services.ApiServices.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from dotenv import load_dotenv
from datetime import date

from backend.services.Filterservices.WosLinkService import WosLinkService


class WOSService(PaperRestService):
    def __init__(self, vhbRanking, abdcRanking):
        load_dotenv()
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        self.vhbRanking = vhbRanking
        self.abdcRanking = abdcRanking

    def query(self, search_term: str, filters) -> list[PaperDTO]:
        headers = {'X-ApiKey': self.api_key, 'Accept': 'application/json'}
        today = date.today()
        formated_date = today.strftime("%Y-%m-%d")
        q = f"TS=({search_term})" # TS = Topic search in WoS
    
        if filters.start_year and filters.end_year:
            q += f" AND DOP={filters.start_year}/{filters.end_year}"
        elif filters.start_year and not filters.end_year:
            
            q += f" AND DOP={filters.start_year}/{formated_date}"
        elif filters.end_year and not filters.start_year:
            q += f" AND DOP=1000/{filters.end_year}"
        
       # q+= " AND limit=50"
        params = {
            'db': 'WOK',
            'q': q,
            'limit': 50,
        }

        results: list[PaperDTO] = []

        try:
            response = requests.get(self.base_url, headers=headers, params=params)

            response.raise_for_status()
            data = response.json()


            hits = data.get("hits", [])

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
                    source='WOS',
                    sources={'WOS'},
                    source_count= 1,
                    vhbRanking=self.vhbRanking.getRanking(journal, issn),
                    abdcRanking= self.abdcRanking.getRanking(journal, issn),
                    journal_name=journal,
                    issn=issn,
                    eissn=eissn,
                    doi=WosLinkService.get_doi_link(hit),
                    url=WosLinkService.get_wos_url(hit),
                    citations=citations
                )

                print(f"[DEBUG] Paper: {paper.title} | Journal: {paper.journal_name} | ISSN: {issn} | VHB-Ranking: {paper.vhbRanking}")
                results.append(paper)

        except requests.exceptions.RequestException as e:
          print(f"[WOS API Fehler]: {e}")

        return results



    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return self.query(searchTerm, filters)



