# services/openalex_service.py
# OpenAlex-API-Abfrage

import requests
from typing import List, Optional
from backend.models.FilterCriteria import FilterCriteria
from backend.services.ApiServices.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO


class OpenAlexService(PaperRestService):
    def __init__(self, vhbRanking, abdcRanking): #neu Finja
        self.base_url = "https://api.openalex.org/works"
        self.vhbRanking = vhbRanking #neu Finja
        self.abdcRanking = abdcRanking

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

            # print(json.dumps(data, indent=2))


            for result in data.get('results', []):
                doi = result.get('doi')
                clean_doi = doi.replace("https://doi.org/", "") if doi else None
                primary_location = result.get('primary_location', {})
                source = result.get('host_venue', {})

                url = (primary_location.get('url') if isinstance(primary_location, dict) else None) or (f"https://doi.org/{clean_doi}" if clean_doi else None)

                # Reconstruct abstract from inverted index
                abstract_index = result.get('abstract_inverted_index')
                if isinstance(abstract_index, dict):
                    abstract_words = sorted(abstract_index.items(), key=lambda x: min(x[1]))
                    abstract = ' '.join(word for word, _ in abstract_words)
                else:
                    abstract = 'N/A'

                paper = PaperDTO(
                    title=result.get('title', 'N/A'),
                    authors = [
                        a.get('author', {}).get('display_name', 'N/A')
                        for a in result.get('authorships', [])
                    ] if result.get('authorships') else [], 
                    abstract=abstract,
                    date=result.get('publication_date', '1900-01-01'),
                    source='OpenAlex',
                    vhbRanking= self.vhbRanking.getRanking(source.get('issn_l',source.get('display_name'))),
                    abdcRanking=self.abdcRanking.getRanking(source.get('issn_l', source.get('display_name'))),
                    journal_name=source.get('display_name'),
                    issn=source.get('issn_l'),
                    eissn=None,
                    doi=doi,
                    url=url,
                    citations=result.get('cited_by_count', 0)
                )

                print(f"[DEBUG] Paper: {paper.title} | Journal: {paper.journal_name} | ISSN: {paper.issn} | VHB-Ranking: {paper.vhbRanking}")
                results.append(paper)

        except requests.exceptions.RequestException as e:
            print(f"[OpenAlex API Fehler]: {e}")

        return results

    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return self.query(searchTerm, filters)
