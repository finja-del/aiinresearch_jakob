# services/openalex_service.py
# OpenAlex-API-Abfrage

import requests
from typing import List, Optional
from backend.models.FilterCriteria import FilterCriteria
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO


class OpenAlexService(PaperRestService):
    def __init__(self, ranking): #neu Finja
        self.base_url = "https://api.openalex.org/works"
        self.ranking = ranking #neu Finja

    def query(self, search_term: str, filter_criteria: Optional[FilterCriteria] = None) -> List[PaperDTO]:
        params = {
            'search': search_term,
            'per-page': '25',
        }

        # Baue Filter ein (Publikationsjahre, Sprache, Autor)
        filters = []
        if filter_criteria:
            if filter_criteria.start_year and filter_criteria.end_year:
                filters.append(f"from_publication_date:{filter_criteria.start_year}-01-01")
                filters.append(f"to_publication_date:{filter_criteria.end_year}-12-31")
            # if filter_criteria.author:
            #     filters.append(f"author.display_name.search:{filter_criteria.author}")
            # Sprache ist optional und nicht direkt unterstützt → OpenAlex indexiert meist nur englisch explizit

            if filters:
                params['filter'] = ','.join(filters)

        results: List[PaperDTO] = []

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            for result in data.get('results', []):
                doi = result.get('doi')
                primary_location = result.get('primary_location', {})
                source = result.get('host_venue', {})

                # Reconstruct abstract from inverted index
                abstract_index = result.get('abstract_inverted_index')
                if isinstance(abstract_index, dict):
                    abstract_words = sorted(abstract_index.items(), key=lambda x: min(x[1]))
                    abstract = ' '.join(word for word, _ in abstract_words)
                else:
                    abstract = 'N/A'

                results.append(PaperDTO(
                    title=result.get('title', 'N/A'),
                    authors = [
                        a.get('author', {}).get('display_name', 'N/A')
                        for a in result.get('authorships', [])
                    ] if result.get('authorships') else [], 
                    abstract=abstract,
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

    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return self.query(searchTerm, filters)
