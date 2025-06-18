# services/wos_service.py
# Web of Science API-Anbindung (nur wenn API-Zugang vorhanden)


import requests
import os
from datetime import date
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from dotenv import load_dotenv



class WOSService(PaperRestService):
    def __init__(self, ranking):
        load_dotenv()
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/api/wos"
        self.ranking = ranking #neu Finja


    def query(self, search_term: str) -> list[PaperDTO]:
        headers = {'X-ApiKey': self.api_key, 'Accept': 'application/json'}
        params = {
            'databaseId': 'WOS',
            'usrQuery': search_term,
            'count': '25'
        }

        results: list[PaperDTO] = []

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            for record in data.get('Data', {}).get('Records', {}).get('records', []):
                title = record.get('title', {}).get('value')
                authors = ', '.join([a['full_name'] for a in record.get('authors', [])])
                journal_info = record.get('source', {})

                results.append(PaperDTO(
                    title=title or 'N/A',
                    authors=authors or 'N/A',
                    abstract=record.get('abstract', {}).get('value', 'N/A'),
                    date=record.get('published', {}).get('date', '1900-01-01'),
                    source='WOS',
                    quality_score=0.0,
                    journal_name=journal_info.get('title'),
                    issn=journal_info.get('issn'),
                    eissn=journal_info.get('eissn'),
                    doi=record.get('doi'),
                    url=f"https://doi.org/{record.get('doi')}" if record.get('doi') else None,
                    citations=record.get('times_cited', 0)
                ))
        except requests.exceptions.RequestException as e:
            print(f"[WOS API Fehler]: {e}")
        return results

    def getPaperList(self, searchTerm: str) -> list[PaperDTO]:
        return self.query(searchTerm)
