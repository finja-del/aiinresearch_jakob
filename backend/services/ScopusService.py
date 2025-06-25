# services/scopus_service.py
# Scopus-API-Abfrage mit Fehlerbehandlung
import os
from typing import Optional
from urllib.parse import quote_plus
import requests
from dotenv import load_dotenv
from backend.models.FilterCriteria import FilterCriteria
from services.PaperRestService import PaperRestService
from models.PaperDTO import PaperDTO

class ScopusService(PaperRestService):

    def __init__(self, abc_ranking):  # neu Finja
        load_dotenv()
        self.api_key = os.getenv('SCOPUS.APIKEY')
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.abc_ranking = abc_ranking  # neu Finja

    def build_query(self, search_term: str, filters: Optional[FilterCriteria]) -> str:
        query_parts = [f"TITLE({search_term})"]

        if filters:
            if filters.start_date:
                query_parts.append(f"PUBYEAR > {filters.start_year}")
            if filters.end_date:
                query_parts.append(f"PUBYEAR < {filters.end_year}")
            if filters.author:
                query_parts.append(f"AUTHNAME({filters.author})")
            if filters.language:
                query_parts.append(f"LANGUAGE({filters.language})")


        return " AND ".join(query_parts)

    def query(self, search_term: str, filters: Optional[FilterCriteria]) -> list[PaperDTO]:
        query_string = self.build_query(search_term, filters)
        print(f"[DEBUG] Query: {query_string}")

        params = {
            "query": query_string,
            "count": "25",
        }

        encoded_url = f"{self.base_url}?query={quote_plus(query_string)}&count=25"
        print(f"[DEBUG] Manuell zusammengesetzte URL: {encoded_url}")

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
            print("[DEBUG] Results gefunden:", len(data.get("search-results", {}).get("entry", [])))

            for result in data.get("search-results", {}).get("entry", []):
                journal_name = result.get("prism:publicationName", "N/A")
                abc_ranking = self.abc_ranking.match_ranking(journal_name)
                results.append(PaperDTO(
                    title=result.get("dc:title", "N/A"),
                    authors=result.get("dc:creator", "N/A"),
                    abstract=result.get("dc:description", "N/A"),
                    date=result.get("prism:coverDate", "1900-01-01"),
                    source="Scopus",
                    quality_score=abc_ranking,
                    journal_name=result.get("prism:publicationName", "N/A"),
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
