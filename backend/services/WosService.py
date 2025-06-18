# services/wos_service.py
# Web of Science API-Anbindung (nur wenn API-Zugang vorhanden)


import requests
import os
from datetime import date
from services.PaperRestService import PaperRestService
from models.PaperDTO import PaperDTO
from dotenv import load_dotenv



class WOSService(PaperRestService):
    def __init__(self, ranking):
        load_dotenv()
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        self.ranking = ranking #neu Finja


    def query(self, search_term: str) -> list[PaperDTO]:
        headers = {'X-ApiKey': self.api_key, 'Accept': 'application/json'}
        params = {
            'db': 'WOK',
            'q': f'TI={search_term}'
        }

        results: list[PaperDTO] = []

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            for result in data.get('resulsts', []):
                doi = result.get('doi')
                primary_location = result.get('primary_location', {})
                source = result.get('host_venue', {})

                results.append(PaperDTO(
                   title=result.get('title', 'N/A'),
                    authors=', '.join(
                        a.get('author', {}).get('display_name', 'N/A') for a in result.get('authorships', [])),
                    abstract=result.get('abstract', 'N/A'),
                    date=result.get('publication_date', '1900-01-01'),
                    source='OpenAlex',
                    quality_score=0.0,
                    journal_name=source.get('display_name'),
                    issn=source.get('issn_l'),
                    eissn=None,
                    doi=doi,
                    url=primary_location.get('url') or (f"https://doi.org/{doi}" if doi else None),
                    citations=result.get('cited_by_count', 0)
                ))
        except requests.exceptions.RequestException as e:
            print(f"[WOS API Fehler]: {e}")
        return results

    def getPaperList(self, searchTerm: str) -> list[PaperDTO]:
        return self.query(searchTerm)
