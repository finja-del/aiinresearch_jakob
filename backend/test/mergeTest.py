#!/usr/bin/env python
"""
Metrik: Wie viele Duplikate entfernt DuplicateMergeService auf echten Daten?
"""

from collections import Counter
from backend.models.FilterCriteria import FilterCriteria
from backend.services.ApiServices.ScopusService import ScopusService
from backend.services.ApiServices.OpenAlexService import OpenAlexService
from backend.services.ApiServices.WosService import WosService
from backend.services.Deduplication.DuplicateMergeService import DuplicateMergeService

# ----------- Settings ----------
SEARCH_TERM   = "corporate social responsibility"  # Suchbegriff
MAX_PER_SRC   = 100          # pro Quelle
filter_crit   = FilterCriteria(start_year=2010, end_year=2010)   # ggf. Jahresfilter setzen
dummy_rank    = type("Dummy", (), {"getRanking": lambda *_: None})()
# --------------------------------

def collect():
    sources = {}
    for svc_cls, label in [
        (ScopusService, "Scopus"),
        (OpenAlexService, "OpenAlex"),
        (WosService, "WOS"),
    ]:
        svc = svc_cls(dummy_rank, dummy_rank)
        lst = svc.getPaperList(SEARCH_TERM, filter_crit)[:MAX_PER_SRC]
        print(f"{label}: {len(lst)} Paper geholt")
        for p in lst:
            # Set the sources set to exactly this label (no duplicates per source list)
            p.sources = {label}
            p.sourceCount = 1
        sources[label] = lst
    return sources

def main():
    src_lists = collect()
    all_raw   = sum(src_lists.values(), [])      # flache Liste
    raw_count = len(all_raw)

    merged    = DuplicateMergeService.merge_duplicates(all_raw)
    merged_count = len(merged)

    # --- Quellen bereinigen & sourceCount korrekt setzen ---
    for p in merged:
        raw_sources = p.get("sources", [])
        if not isinstance(raw_sources, list):
            raw_sources = list(raw_sources)
        unique_sources = list(set(raw_sources))
        p["sources"] = unique_sources
        p["sourceCount"] = len(unique_sources) or 1

    print("\n--- Ergebnis ---")
    print(f"Rohtreffer     : {raw_count}")
    print(f"Nach Merging   : {merged_count}")
    print(f"Reduktion      : {100 * (1 - merged_count / raw_count):.1f}%")

    # Verteilung nach sourceCount
    dist = Counter(p.get('sourceCount', 1) for p in merged)

    print("\nVerteilung nach Anzahl Quellen pro Paper:")
    total_contributions = 0
    for k in sorted(dist):
        print(f"  {k} Quelle(n): {dist[k]} Paper")
        total_contributions += k * dist[k]

    print(f"\nGesamtbeiträge vor Merge (hochgerechnet aus sourceCount): "
          f"{total_contributions}")

if __name__ == "__main__":
    main()
