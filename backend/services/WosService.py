# services/wos_service.py
# Web of Science API-Anbindung (nur wenn API-Zugang vorhanden)


import requests
import os
from datetime import date
from typing import List
from backend.models import FilterCriteria
from backend.services.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from dotenv import load_dotenv



class WOSService(PaperRestService):
    def __init__(self, ranking):
        load_dotenv()
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        self.ranking = ranking #neu Finja


    def build_query(self, search_term: str, filters: FilterCriteriaDTO) -> str:
        query_parts = [f"TS=({search_term})"]  # TS = Topic search in WoS

        if filters.start_year and filters.end_year:
            query_parts.append(f"PY=({filters.start_year}-{filters.end_year})")
        elif filters.start_year:
            query_parts.append(f"PY=({filters.start_year}-*)")
        elif filters.end_year:
            query_parts.append(f"PY=(1900-{filters.end_year})")

        if filters.author:
            query_parts.append(f"AU=({filters.author})")
        if filters.language:
            query_parts.append(f"LA=({filters.language})")

        return " AND ".join(query_parts)

    def query(self, search_term: str, filters: FilterCriteriaDTO) -> List[PaperDTO]:
        query_string = self.build_query(search_term, filters)
        print(f"[DEBUG] WoS Query: {query_string}")

        headers = {
            "X-ApiKey": self.api_key,
            "Accept": "application/json"
        }

        params = {
            "databaseId": "WOK",
            "usrQuery": query_string,
            "count": 25
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            print(f"[DEBUG] URL: {response.url}")
            response.raise_for_status()
            data = response.json()
            entries = data.get("Data", {}).get("Records", {}).get("records", [])

            results = []
            for record in entries:
                static_data = record.get("static_data", {})
                summary = static_data.get("summary", {})
                titles = summary.get("titles", {}).get("title", [])
                title = titles[0].get("content") if titles else "N/A"
                source = summary.get("source", {}).get("source_title", "")

                results.append(PaperDTO(
                    title=title,
                    authors="; ".join(a.get("full_name") for a in static_data.get("contributors", {}).get("authors", {}).get("author", [])),
                    abstract=static_data.get("abstracts", {}).get("abstract", {}).get("abstract_text", "N/A"),
                    date=summary.get("pub_info", {}).get("pubyear", "1900"),
                    source="WOS",
                    quality_score=0.0,
                    journal_name=source,
                    issn=summary.get("pub_info", {}).get("issn", None),
                    eissn=None,
                    doi=summary.get("doi", {}).get("content", None),
                    url=None,
                    citations=summary.get("pub_info", {}).get("times_cited", 0)
                ))
            return results

        except requests.exceptions.RequestException as e:
            print(f"[WOS API Fehler]: {e}")
            return []

    def getPaperList(self, searchTerm: str, filters: FilterCriteriaDTO) -> list[PaperDTO]:
        return self.query(searchTerm, filters)
