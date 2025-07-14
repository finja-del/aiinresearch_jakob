"""
Test: DuplicateMergeService muss nach dem Mergen eine konsistente
Quellensumme liefern:  sum(sourceCount_i) == #rohe Paper.
"""

import pytest
from backend.models.PaperDTO import PaperDTO
from backend.services.Deduplication.DuplicateMergeService import DuplicateMergeService

# ---------- Hilfs-Factory ---------- #
def mk(title: str, doi: str | None, src: str) -> PaperDTO:
    """
    Erzeugt ein minimalistisches PaperDTO mit genau einem
    Quellen-Set → {src} und sourceCount = 1
    """
    return PaperDTO(
        title=title,
        doi=doi,
        date="2010",
        source=src,
        sources={src},
        source_count=1,
        authors=[], abstract="", vhbRanking=None, abdcRanking=None
    )

def test_merge_consistency():
    # --- Rohdaten simulieren ---------------------------------------------
    raw = [
        mk("A Paper", "10.111/a", "Scopus"),
        mk("A Paper", "10.111/a", "OpenAlex"),        # Duplikat (DOI)
        mk("B Paper", None,       "Scopus"),
        mk("B Paper", None,       "WOS"),             # Duplikat (Titel+Jahr)
        mk("C Paper", None,       "Scopus"),
        mk("C  Paper", None,      "OpenAlex"),        # Fuzzy-Match (>90 %)
        mk("Unique",  None,       "Scopus"),          # bleibt allein
    ]
    raw_count = len(raw)                       # -> 7

    merged = DuplicateMergeService.merge_duplicates(raw)

    # ----------- 1) Grundasserts -----------------------------------------
    assert len(merged) == 4, "Es sollten 3 Duplikat-Gruppen zusammengelegt sein."

    # ----------- 2) Summe Quellen × Paper == raw_count -------------------
    total_contrib = sum(p["sourceCount"] for p in merged)
    assert total_contrib == raw_count, (
        f"sourceCount-Summe ({total_contrib}) ≠ Roh-Treffer ({raw_count})"
    )

    # ----------- 3) Jede Gruppe hat saubere Quellenliste -----------------
    for p in merged:
        assert len(p["sources"]) == len(set(p["sources"])), (
            f"Doppelte Labels in sources-Liste bei: {p['title']}"
        )