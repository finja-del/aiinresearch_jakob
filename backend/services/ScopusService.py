# scopus_service.py – überarbeitet für POST + FilterCriteria
import os
from typing import Optional
from urllib.parse import quote_plus
import requests
from dotenv import load_dotenv
from backend.models.FilterCriteria import FilterCriteria
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
import json

class ScopusService(PaperRestService):

    def __init__(self, abc_ranking):
        load_dotenv()
        self.api_key = os.getenv('SCOPUS.APIKEY')
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.abc_ranking = abc_ranking  # enthält Ranking-Logik (z. B. VHB, ABDC)

    def build_query(self, search_term: str, filters: Optional[FilterCriteria]) -> str:
        query_parts = [f"TITLE({search_term})"]

        if filters:
            if filters.start_year:
                query_parts.append(f"PUBYEAR > {filters.start_year - 1}")  # simuliert >=

            if filters.end_year:
                query_parts.append(f"PUBYEAR < {filters.end_year + 1}")    # simuliert <=


            # if filters.author:
            #     author_queries = [f"AUTHNAME({a})" for a in filters.author]
            #     query_parts.append(f"({' OR '.join(author_queries)})")

            # if filters.language:
            #     language_queries = [f"LANGUAGE({l})" for l in filters.language]
            #     query_parts.append(f"({' OR '.join(language_queries)})")

        query = " AND ".join(query_parts)
        print(f"[DEBUG] Final Scopus Query: {query}")
        return query

    def query(self, search_term: str, filters: Optional[FilterCriteria]) -> list[PaperDTO]:
        print("[DEBUG] ScopusService.query() wurde aufgerufen")

        query_string = self.build_query(search_term, filters)

        encoded_url = f"{self.base_url}?query={quote_plus(query_string)}&count=25"
        print(f"[DEBUG] Scopus API URL: {encoded_url}")

        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }

        results: list[PaperDTO] = []

        try:
            response = requests.get(encoded_url, headers=headers)
            print(f"[DEBUG] Response Code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(json.dumps(data, indent=2))  # Debug-Ausgabe der gesamten Antwort

            entries = data.get("search-results", {}).get("entry", [])
            print(f"[DEBUG] Results gefunden: {len(entries)}")

            for result in entries:
                journal_name = result.get("prism:publicationName", "N/A")
                ranking_score = self.abc_ranking.match_ranking(journal_name)  # kann später umgebaut werden

                results.append(PaperDTO(
                    title=result.get("dc:title", "N/A"),
                    authors=[result.get("dc:creator")] if result.get("dc:creator") else [],
                    abstract=result.get("dc:description", "N/A"),
                    date=result.get("prism:coverDate", "1900-01-01"),
                    source="Scopus",
                    quality_score=ranking_score,
                    journal_name=journal_name,
                    issn=result.get("prism:issn"),
                    eissn=result.get("prism:eIssn"),
                    doi=result.get("prism:doi"),
                    url=result.get("prism:url"),
                    citations=int(result.get("citedby-count", 0))
                ))
        except requests.exceptions.RequestException as e:
            print(f"[Scopus API Fehler]: {e}")

        return results

    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return self.query(searchTerm, filters)
