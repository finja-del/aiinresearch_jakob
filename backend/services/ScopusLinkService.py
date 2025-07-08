# backend/services/ScopusLinkService.py
class ScopusLinkService:
    """Hilfsfunktionen, um DOI- und Scopus-Web-Links aus einem Scopus-API-Eintrag zu extrahieren."""

    @staticmethod
    def get_doi_link(result: dict) -> str:
        """Gibt einen klickbaren DOI-Link zurück (https://doi.org/...), falls vorhanden."""
        doi = result.get("prism:doi")
        return f"https://doi.org/{doi}" if doi else ""

    @staticmethod
    def get_scopus_url(result: dict) -> str:
        """
        Gibt den Link zur Scopus-Webseite des Papers zurück.
        Sucht zunächst in 'link'-Elementen nach rel='scopus',
        fällt auf prism:url zurück, wenn nichts gefunden wird.
        """
        links = result.get("link", [])
        if isinstance(links, list):
            for link in links:
                rel = link.get("@ref") or link.get("@rel")
                if rel and rel.lower() == "scopus":
                    return link.get("@href")
        return result.get("prism:url", "")