# scopus_service.py – überarbeitet für POST + FilterCriteria
import os
from typing import Optional
from urllib.parse import quote_plus
import requests
from dotenv import load_dotenv
from backend.models.FilterCriteria import FilterCriteria
from backend.services.ApiServices.PaperRestService import PaperRestService
from backend.models.PaperDTO import PaperDTO
from backend.services.Filterservices.ScopusLinkService import ScopusLinkService


class ScopusService(PaperRestService):

    def __init__(self, vhbRanking, abcRanking):
        load_dotenv()
        self.api_key = os.getenv('SCOPUS.APIKEY')
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.vhbRanking = vhbRanking
        self.abdcRanking = abcRanking

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

        # 1 Credit:
        #encoded_url = f"{self.base_url}?query={quote_plus(query_string)}&count=200"
        # 2Credits:
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
            #print(json.dumps(data, indent=2))  # Debug-Ausgabe der gesamten Antwort

            entries = data.get("search-results", {}).get("entry", [])
            print(f"[DEBUG] Results gefunden: {len(entries)}")

            for result in entries:
                journal_name = result.get("prism:publicationName", "N/A")
                issn = result.get("prism:issn", "N/A")
                vhbScore = self.vhbRanking.getRanking(journal_name, issn)
                abdcScore = self.abdcRanking.getRanking(journal_name, issn)
                paper = PaperDTO(
                    title=result.get("dc:title", "N/A"),
                    authors=[result.get("dc:creator")] if result.get("dc:creator") else [],
                    abstract=result.get("dc:description", "N/A"),
                    date=result.get("prism:coverDate", "1900-01-01"),
                    source="Scopus",
                    sources={"Scopus"},
                    source_count=1,
                    vhbRanking=vhbScore,
                    abdcRanking=abdcScore,
                    journal_name=journal_name,
                    issn=result.get("prism:issn"),
                    eissn=result.get("prism:eIssn"),
                    doi=ScopusLinkService.get_doi_link(result),
                    url=ScopusLinkService.get_doi_link(result),
                    citations=int(result.get("citedby-count", 0))
                )

                #if paper.vhbRanking != "N/A":
                 #   print(f"[DEBUG] Paper: {paper.title} | Journal: {journal_name} | ISSN: {issn} | VHB-Ranking: {vhbScore}")
                #if paper.abdcRanking != "N/A":
                 #   print(f"[DEBUG] Paper: {paper.title} | Journal: {journal_name} | ISSN: {issn} | ABDC-Ranking: {abdcScore}")

                results.append(paper)

        except requests.exceptions.RequestException as e:
            print(f"[Scopus API Fehler]: {e}")

        return results

    def getPaperList(self, searchTerm: str, filters: FilterCriteria) -> list[PaperDTO]:
        return self.query(searchTerm, filters)
