# tests/test_search_controller.py
import pytest
from backend.controller.SearchController import SearchController
from backend.models.FilterCriteria import FilterCriteria
from backend.models.PaperDTO import PaperDTO

class DummyClient:
    def __init__(self, name, papers):
        self._papers = papers
        DynamicClass = type(f"{name}Service", (object,), {
            "getPaperList": lambda self, q, f: self._papers
        })
        self.__class__ = DynamicClass

def make_paper(title, journal, issn, source):
    paper = PaperDTO(
        title=title,
        doi=None,
        authors=[],
        abstract="",
        date="2024-01-01",
        source=source,
        vhbRanking=None,
        abdcRanking=None,
    )
    # fehlende Felder direkt am Objekt ergänzen
    paper.journal = journal
    paper.issn = issn
    return paper

def test_search_controller_deduplication(monkeypatch):
    p1 = make_paper("Same", "JIBS", ["1111-1111"], "Scopus")
    p2 = make_paper("Same", "JIBS", ["1111-1111"], "WebOfScience")
    scopus = DummyClient("Scopus", [p1])
    wos    = DummyClient("WebOfScience", [p2])

    controller = SearchController()
    # Patching die echten Services
    monkeypatch.setattr(controller, "scopus", scopus)
    monkeypatch.setattr(controller, "wos", wos)
    controller.apiClients = [scopus, wos]  # um checkServices zu umgehen

    filters = FilterCriteria(scopus=True, wos=True, openalex=False)
    results = controller.searchPapers("irrelevant", filters)

    assert len(results) == 1
    assert "Scopus" in results[0]["source"]
    assert "WebOfScience" in results[0]["source"]