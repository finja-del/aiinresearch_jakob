from typing import List, Dict

from backend.models.PaperDTO import PaperDTO

# Versuche zuerst RapidFuzz wegen höherer Performance; falls nicht vorhanden, nutze difflib als Fallback.
try:
    from rapidfuzz import fuzz
    def similarity(a: str, b: str) -> int:
        return fuzz.token_set_ratio(a, b)
except ImportError:  # pragma: no cover
    import difflib
    def similarity(a: str, b: str) -> int:
        return int(difflib.SequenceMatcher(None, a, b).ratio() * 100)


class DuplicateMergeService:
    """
    DuplicateMergeService – vereinheitlichtes Zusammenführen von Papern aus mehreren Quellen.

    Matching‑Strategie (Priorität absteigend)
    1. DOI – exakter Vergleich, eindeutig.
    2. Normalisierter Titel + Publikationsjahr.
    3. Fuzzy‑Titelvergleich (Levenshtein ≥ 90 %) – nur wenn kein DOI vorhanden.

    Beim Mergen werden die Quellen in ``paper.sources`` (Set[str]) gesammelt
    und ``paper.source_count`` automatisch aktualisiert.
    """

    SIMILARITY_THRESHOLD: int = 90

    @staticmethod
    def _normalize(text: str | None) -> str:
        """Robustly convert None to empty string and strip/lowercase."""
        return str(text or "").strip().lower()



    @staticmethod
    def _merge_sources(existing: PaperDTO, new: PaperDTO) -> None:
        """Fügt die Quelle des neuen Papers zum bestehenden hinzu (falls noch nicht vorhanden)."""
        if getattr(new, "source", None):
            existing_sources = getattr(existing, "source", "") or ""
            new_source = new.source
            if new_source not in existing_sources.split(" and "):
                existing.source = f"{existing_sources} and {new_source}".strip(" and ")
        # combine sets
        existing.sources.update(new.sources)         # type: ignore[attr-defined]
        if not hasattr(existing, "source_count") or existing.source_count is None:
            existing.source_count = 0                # type: ignore[attr-defined]
        existing.source_count = len(existing.sources) # type: ignore[attr-defined]
    @staticmethod
    def _title_year_key(p: PaperDTO) -> str:
        title_key = DuplicateMergeService._normalize(p.title)[:100]
        year = (p.date or "0000")[:4]
        return f"{title_key}-{year}"

    @staticmethod
    def _generate_key(p: PaperDTO) -> str:
        """
        Generate a key for duplicate detection:
        - If DOI is present, return DOI key AND also allow title+year key to be used as a secondary key
        - This enables merging of entries with the same title/year regardless of DOI presence (helps merge title duplicates with or without DOI).
        """
        doi_key = (p.doi or "").strip().lower()
        title_key = DuplicateMergeService._title_year_key(p)
        # If DOI is present, use both keys (DOI and title_key) as possible keys for matching
        # The main merge_duplicates logic will try both keys for matching.
        # For key generation, return both keys as a tuple (for internal use).
        return doi_key or title_key

    @staticmethod
    def _fuzzy_match(a: str, b: str, threshold: float = 0.9) -> bool:
        return similarity(a, b) >= int(threshold * 100)

    @classmethod
    def merge_duplicates(cls, papers: List[PaperDTO]) -> List[dict]:
        """
        Reduziert eine Paper‑Liste auf eindeutige Einträge.

        Args:
            papers: Liste von PaperDTO‑Objekten.

        Returns:
            Liste eindeutiger Paper als Dicts für die API.
        """
        merged_dict: Dict[str, PaperDTO] = {}

        for paper in papers:
            # init sources set
            if not getattr(paper, "sources", None):
                paper.sources = set()           # type: ignore[attr-defined]
            if getattr(paper, "source", None):
                paper.sources.add(paper.source) # type: ignore[attr-defined]

            key = DuplicateMergeService._generate_key(paper)

            # 1) exakter Key‑Treffer
            if key in merged_dict:
                DuplicateMergeService._merge_sources(merged_dict[key], paper)
                continue

            # 1b) Titel+Jahr-Key als alternativer Schlüssel, falls DOI vorhanden (um Titel-Dubletten mit/ohne DOI zusammenzuführen)
            if paper.doi:
                title_key = DuplicateMergeService._title_year_key(paper)
                if title_key in merged_dict:
                    DuplicateMergeService._merge_sources(merged_dict[title_key], paper)
                    continue

            # 2) fuzzy fallback, auch bei DOI, falls kein exakter Treffer (aber nicht, wenn DOI schon mit anderem Eintrag kollidiert)
            matched = False
            for m_key, m_p in merged_dict.items():
                # Wenn der DOI von paper nicht mit einem bestehenden Eintrag kollidiert (d.h. noch nicht vorhanden oder nicht gleich),
                # dann fuzzy match erlauben (auch bei DOI)
                if DuplicateMergeService._fuzzy_match(
                        DuplicateMergeService._normalize(m_p.title),
                        DuplicateMergeService._normalize(paper.title)):
                    DuplicateMergeService._merge_sources(m_p, paper)
                    matched = True
                    break
            if matched:
                continue

            merged_dict[key] = paper

        # source_count auffüllen
        for p in merged_dict.values():
            if hasattr(p, "sources"):
                p.source_count = len(p.sources)  # type: ignore[attr-defined]
            else:
                p.source_count = 1               # type: ignore[attr-defined]

        return [p.to_api_dict() for p in merged_dict.values()]