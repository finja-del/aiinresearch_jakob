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
    Ermittelt und verschmilzt doppelte Paper‑Einträge aus verschiedenen Quellen.

    Matching‑Strategie (absteigende Priorität):
    1. **ISSN**   – exakter String‑Vergleich oder Überschneidung mehrerer ISSN‑Einträge.
    2. **Titel + Journal** – beide Strings exakt gleich (case‑insensitive, Whitespace getrimmt).
    3. **Fuzzy‑Matching**  – Ähnlichkeitsmaß (RapidFuzz token_set_ratio oder difflib) >= 90 %.
    """

    SIMILARITY_THRESHOLD: int = 90

    @staticmethod
    def _normalize(text: str | None) -> str:
        return (text or "").strip().lower()

    @classmethod
    def _is_duplicate(cls, p1: PaperDTO, p2: PaperDTO) -> bool:
        """Prüft, ob zwei Paper identisch sind."""
        # 1️⃣ ISSN‑Vergleich
        issn1 = {cls._normalize(i) for i in (p1.issn or [])} if isinstance(p1.issn, list) else {cls._normalize(p1.issn)}
        issn2 = {cls._normalize(i) for i in (p2.issn or [])} if isinstance(p2.issn, list) else {cls._normalize(p2.issn)}
        if issn1 & issn2 - {""}:
            return True

        # 2️⃣ Titel + Journal exakt
        if cls._normalize(p1.title) == cls._normalize(p2.title) and \
           cls._normalize(p1.journal) == cls._normalize(p2.journal):
            return True

        # 3️⃣ Fuzzy‑Matching (Titel & Journal separat, beide über Schwelle)
        title_sim = similarity(cls._normalize(p1.title), cls._normalize(p2.title))
        journal_sim = similarity(cls._normalize(p1.journal), cls._normalize(p2.journal))
        return title_sim >= cls.SIMILARITY_THRESHOLD and journal_sim >= cls.SIMILARITY_THRESHOLD

    @staticmethod
    def _merge_sources(existing: PaperDTO, new: PaperDTO) -> None:
        """Fügt die Quelle des neuen Papers zum bestehenden hinzu (falls noch nicht vorhanden)."""
        if getattr(new, "source", None):
            existing_sources = getattr(existing, "source", "") or ""
            new_source = new.source
            if new_source not in existing_sources.split(" and "):
                existing.source = f"{existing_sources} and {new_source}".strip(" and ")

    @classmethod
    def merge_duplicates(cls, papers: List[PaperDTO]) -> List[dict]:
        """
        Reduziert eine Paper‑Liste auf eindeutige Einträge.

        Args:
            papers: Liste von PaperDTO‑Objekten.

        Returns:
            Liste eindeutiger Paper als Dicts für die API.
        """
        merged: List[PaperDTO] = []

        for paper in papers:
            # Prüfe, ob dieses Paper schon in merged existiert
            duplicate_found = False
            for existing in merged:
                if cls._is_duplicate(paper, existing):
                    cls._merge_sources(existing, paper)
                    duplicate_found = True
                    break

            if not duplicate_found:
                merged.append(paper)

        return [paper.to_api_dict() for paper in merged]