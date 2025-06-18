#neu Finja
import sys
import os

# Damit du auf das models-Modul zugreifen kannst
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.Ranking import Ranking

# 📂 Zukunftssicherer Pfad zur CSV-Datei
base_path = os.path.dirname(__file__)  # Pfad zu tests/test_ranking.py
csv_path = os.path.join(base_path, '..', 'data', 'abc_ranking.csv')

# CSV-Datei laden
ranking = Ranking(csv_path)

# Ein Test-Paper mit Journalname
test_journal = "Abacus"

# Methode aufrufen
result = ranking.match_ranking(test_journal)

# Ausgabe
print(f"📄 Journal: {test_journal} → Ranking: {result}")
