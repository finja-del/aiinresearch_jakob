#new Finja
import csv

class Ranking:
    def __init__(self, filepath):
        self.ranking_data = self._load_ranking(filepath)

    def _load_ranking(self, filepath):
        ranking = {}
        with open(filepath, newline='', encoding='latin1') as csvfile:
            lines = csvfile.readlines()

        # 1. Find the row with the real column headings
        header_index = None
        for i, line in enumerate(lines):
            if "Journal Title" in line and "2022 rating" in line:
                header_index = i
                break

        if header_index is None:
            raise ValueError("No valid header line found with 'Journal Title' and '2022 rating'")

        # 2. Use only the data from this line onwards
        data_lines = lines[header_index:]
        reader = csv.DictReader(data_lines, delimiter=';')

        for row in reader:
            journal = row['Journal Title'].strip().lower()
            rating = row['2022 rating'].strip()
            if journal:  #only valid names
                ranking[journal] = rating

        return ranking

    def match_ranking(self, journal_name: str):
        if not journal_name:
            return None
        key = journal_name.strip().lower()
        return self.ranking_data.get(key, None)

