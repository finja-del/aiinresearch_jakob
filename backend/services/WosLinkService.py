# backend/services/WosLinkService.py

class WosLinkService:
    """
    Hilfsfunktionen, um DOI- und Web-of-Science-Links aus einem einzelnen
    WoS-API-Treffer (dict) zu extrahieren.

    Erwartetes Key-Layout (Beispiele):
      hit["identifiers"]["doi"]              -> "10.1000/example.42"
      hit["links"] = [
          {"type": "full-record", "url": "https://www.webofscience.com/..."},
          ...
      ]
      hit["uid"]  -> "WOS:000123456789"
      hit["UT"]   -> "WOS:000123456789"
    """

    @staticmethod
    def get_doi_link(hit: dict) -> str:
        """
        Liefert einen klickbaren DOI-Link (https://doi.org/...) oder
        einen leeren String, falls kein DOI vorhanden ist.
        """
        doi = hit.get("identifiers", {}).get("doi")
        return f"https://doi.org/{doi}" if doi else ""

    @staticmethod
    def get_wos_url(hit: dict) -> str | None:
        """
        Liefert die URL zur Full-Record-Ansicht in Web of Science.

        Suchreihenfolge:
        1. Link-Eintrag mit type == 'full-record'
        2. UID/UT-Fallback: https://www.webofscience.com/wos/woscc/full-record/<UID>
        """
        links = hit.get("links", [])
        if isinstance(links, list):
            for link in links:
                if str(link.get("type", "")).lower().replace("_", "-") in {
                    "full-record",
                    "fullrecord",
                    "full-record",
                }:
                    return link.get("url")

        uid = hit.get("uid") or hit.get("UT") or hit.get("id")
        if uid:
            return f"https://www.webofscience.com/wos/woscc/full-record/{uid}"

        return None