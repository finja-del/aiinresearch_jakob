import pytest
from backend.services.VhbService import VhbService

vhb = VhbService()  # nimmt Default-JSON


def test_hyphen_vs_plain():
    assert vhb.getRanking("", "1619-4500") == "C"
    assert vhb.getRanking("", "16194500") == "C"


def test_check_digit_x():
    assert vhb.getRanking("", "1537-260X") == "B"


def test_print_vs_online():
    """
    Prüft, dass p-ISSN („1619-4500“) und e-ISSN („16194500“)
    zum gleichen Ranking führen – selbst wenn das Ergebnis 'N/A' ist.
    """
    ranking_print = vhb.getRanking("", "1619-4500")
    ranking_online = vhb.getRanking("", "16194500")

    # Erwartung: beide identisch – ob 'B', 'N/A' oder etwas anderes.
    assert (ranking_print == ranking_online)


@pytest.mark.parametrize(
    "name,expected",
    [
        # 1) Ein paar sichere Treffer aus vhb_journal_ranking.json
        ("Academy of Management Journal (AMJ)", "A+"),
        ("Academy of Management Review (AMR)", "A+"),
        ("Annals of Operations Research", "B"),
    ],)

def test_exact_name_match(name, expected):
    """
    Lookup nur über den Journal-Namen (ISSN leer) muss
    das korrekte Rating liefern.
    """
    assert vhb.getRanking(name, "") == expected


def test_case_insensitive():
    """
    Namen dürfen auch komplett kleingeschrieben werden –
    der Service sollte Groß/Kleinschreibung ignorieren.
    """
    rating_upper = vhb.getRanking("Academy of Management Journal (AMJ)", "")
    rating_lower = vhb.getRanking("academy of management journal (amj)", "")
    assert rating_upper == rating_lower


def test_unknown_name_returns_na():
    """
    Für einen nicht existierenden Namen liefert der Service
    entweder None oder 'N/A' – je nach Implementierung.
    """
    unknown = vhb.getRanking("Very Imaginary Journal of Foo Bar", "")
    assert unknown in (None, "N/A")