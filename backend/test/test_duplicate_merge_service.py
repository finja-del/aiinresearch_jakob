# tests/test_duplicate_merge_service.py
import pytest
from backend.services.Deduplication.DuplicateMergeService import DuplicateMergeService
from backend.models.PaperDTO import PaperDTO
from backend.controller.SearchController import SearchController
from backend.models.FilterCriteria import FilterCriteria
from backend.models.PaperDTO import PaperDTO

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

def test_merge_by_issn():
    a = make_paper("A study", "JMG", ["1234-5678"], "Scopus")
    b = make_paper("Completely different title", "JMG", ["1234-5678"], "WebOfScience")
    merged = DuplicateMergeService.merge_duplicates([a, b])
    assert len(merged) == 1
    assert merged[0]["source"] in {"Scopus and WebOfScience", "WebOfScience and Scopus"}

def test_merge_by_title_and_journal():
    a = make_paper("Strategy", "SMJ", None, "Scopus")
    b = make_paper("strategy", "smj", None, "OpenAlex")
    merged = DuplicateMergeService.merge_duplicates([a, b])
    assert len(merged) == 1

def test_fuzzy_merge():
    a = make_paper("The impact of AI on work", "MISQ", None, "Scopus")
    b = make_paper("Impact of artificial intelligence on work", "MISQ", None, "OpenAlex")
    merged = DuplicateMergeService.merge_duplicates([a, b])
    assert len(merged) == 1