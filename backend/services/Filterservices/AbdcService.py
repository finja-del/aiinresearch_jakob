"""
AbcService
==========

Hilfs‑Service, um ABC‑Ranking‑3 Ratings (A+, A, B, C, D) zu einem Journal
bereitzustellen.  Er wird einmal beim Programmstart initialisiert und dann von
anderen Services (z. B. ScopusService, WosService) für jedes gefundene Paper
aufgerufen.

Vorgehen
--------
1.  Zuerst wird versucht, die (in der Regel eindeutige) ISSN zu matchen.
2.  Falls kein Treffer, wird der Journal‑Titel verglichen (case‑ & whitespace‑
    insensitive).
3.  Wenn beides fehlschlägt ⇒ Rückgabe **"N/A"**.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional, Union
from rapidfuzz import process, fuzz



# Standard‑Pfad relativ zum Projekt‑Root
_DEFAULT_JSON = Path(__file__).resolve().parent.parent.parent / "data" / "abdc_ranking.json"


class AbdcService:
    """Liefert ABC‑Ratings in O(1)."""

    # ------------------------------------------------------------------ #
    # Konstruktor
    # ------------------------------------------------------------------ #
    def __init__(self, ranking_source: Union[str, Path, dict] = _DEFAULT_JSON):
        """
        Parameters
        ----------
        ranking_source : str | Path | dict, optional
            • Pfad zu einer JSON‑Datei,
            • oder bereits geladenes Dict mit den Keys
              ``issn_to_rating`` **und/oder** ``name_to_rating``.
            Wird nichts angegeben, wird die Datei *backend/data/abc_ranking.json*
            verwendet.
        """
        if isinstance(ranking_source, (str, Path)):
            with open(ranking_source, encoding="utf-8") as fh:
                data: dict = json.load(fh)
        elif isinstance(ranking_source, dict):
            data = ranking_source
        else:
            raise TypeError(
                "ranking_source must be a path, str or dict, "
                f"got {type(ranking_source).__name__}"
            )

        # Zwei Lookup‑Tabellen anlegen; Keys direkt normalisieren
        self._issn_to_rating: Dict[str, str] = {
            self._clean_issn(k): v for k, v in data.get("issn_to_rating", {}).items()
        }
        self._name_to_rating: Dict[str, str] = {
            self._norm(k): v for k, v in data.get("name_to_rating", {}).items()
        }

    # ------------------------------------------------------------------ #
    # Öffentliche API
    # ------------------------------------------------------------------ #
    def getRanking(self,
                   journal_title: Optional[str] = None,
                   issn: Optional[str] = None) -> str:
        """
        Liefert das ABC‑Rating für ein Journal.

        Parameters
        ----------
        journal_title : str, optional
        issn          : str, optional

        Returns
        -------
        str
            Das Rating (z. B. ``"A+"``) oder ``"N/A"``.
        """
        # 1) Versuch: ISSN (ohne Bindestrich, Großbuchstaben)
        if issn:
            rating = self._issn_to_rating.get(self._clean_issn(issn))
            if rating:
                return rating

        # 2) Versuch: Titel (Lowercase, kollabierter Whitespace)
        if journal_title:
            normed = self._norm(journal_title)
            rating = self._name_to_rating.get(normed)
            if rating:
                return rating

            # Fuzzy-Match-Versuch

            result = process.extractOne(normed, self._name_to_rating.keys(), scorer=fuzz.ratio)
            if result is not None:
                best_match, score, _ = result
                if score > 90:
                    return self._name_to_rating[best_match]

        return "N/A"

    # Alias für Legacy‑Code
    match_ranking = getRanking  # pragma: no cover

    # ------------------------------------------------------------------ #
    # Helfer
    # ------------------------------------------------------------------ #
    @staticmethod
    def _norm(name: str) -> str:
        """lower‑case + Whitespace reduzieren"""
        return re.sub(r"\s+", " ", name).strip().lower()

    @staticmethod
    def _clean_issn(raw: str) -> str:
        """Bindestrich entfernen und ggf. X groß schreiben."""
        return raw.replace("-", "").upper()

