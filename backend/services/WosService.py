# services/wos_service.py
# Web of Science API-Anbindung (nur wenn API-Zugang vorhanden)


import requests
import os
from datetime import date
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from dotenv import load_dotenv
import json



class WOSService(PaperRestService):
    def __init__(self, ranking):
        load_dotenv()
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        self.ranking = ranking #neu Finja


    def query(self, search_term: str, filters) -> list[PaperDTO]:
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

            print(json.dumps(data, indent=2))

            hits = data.get("hits", [])
            authors =[]
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

                # title = hit.get('title',{})
                # doi = hit.get('identifiers',{}).get('doi')
                # author_objs = hit.get('names', {}).get('authors') or []
                # authors = [a.get('displayName', 'N/A') for a in author_objs]
                # #citation = hit.get("citations",[])[0].get('count')
                # citation_data = hit.get("citations", [])
                # if citation_data and isinstance(citation_data, list):
                #     citations = citation_data[0].get("count", 0)
                # journal = hit.get('source',{}).get('sourceTitle')
                # year = hit.get('source',{}).get('publishYear')
                # eissn = hit.get('identifiers',{}).get('eissn')
                # issn = hit.get('identifiers',{}).get('issn')
                # print(f"Title:{title}   Author/en:{authors}    Citations:{citation}   doi:{doi}  \n  year:{year}  journal:{journal}")

                results.append(PaperDTO(
                #    title=title or 'N/A',
                #     authors=authors or 'N/A',
                #     #abstract='',
                #     abstract = abstract or 'N/A',
                #     date=str(year) if year else "1900",
                #     source ='WOK',
                #     quality_score=0.0,
                #     journal_name=journal,
                #     issn=issn,
                #     eissn=eissn,
                #     doi=doi,
                #     url='',
                #     citations= citation
                # ))
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    date=str(year) if year else "1900",
                    source='WOK',
                    quality_score=0.0,
                    journal_name=journal,
                    issn=issn,
                    eissn=eissn,
                    doi=doi,
                    url=url,
                    citations=citations
                ))
                
                
        except requests.exceptions.RequestException as e:
            print(f"[WOS API Fehler]: {e}")
        return results

    def getPaperList(self, searchTerm: str, filters) -> list[PaperDTO]:
        return self.query(searchTerm, filters)
