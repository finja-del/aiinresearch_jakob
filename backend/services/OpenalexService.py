# services/openalex_service.py
# OpenAlex-API-Abfrage
import requests
from datetime import date
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO


class OpenAlexService(PaperRestService):
    def __init__(self, ranking): #neu Finja
        self.base_url = "https://api.openalex.org/works"
        self.ranking = ranking #neu Finja

    def query(self, search_term: str) -> list[PaperDTO]:
        params = {
            'search': search_term,
            'per-page': '25',
        }
        results: list[PaperDTO] = []

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            for result in data.get('results', []):
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
                    url = (primary_location.get('url') if primary_location else None) or (f"https://doi.org/{doi}" if doi else None),   
                    citations=result.get('cited_by_count', 0)
                ))
        except requests.exceptions.RequestException as e:
            print(f"[OpenAlex API Fehler]: {e}")
        return results

    def getPaperList(self, searchTerm: str) -> list[PaperDTO]:
        return self.query(searchTerm)
