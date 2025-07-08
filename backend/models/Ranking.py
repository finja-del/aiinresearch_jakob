#new Finja
import json

class Ranking:
    def __init__(self, filepath):
        self.ranking_data = self._load_ranking(filepath)
        self.name_to_rating = self.ranking_data.get("name_to_rating", {})
        self.issn_to_rating = self.ranking_data.get("issn_to_rating", {})

    def _load_ranking(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def match_ranking(self, journal):
        if not isinstance(journal, str) or not journal:
            raise TypeError("Expected a non-empty string for journal or ISSN")

        first_char = journal[0]
        ascii_code = ord(first_char)

        if 48 <= ascii_code <= 57: # for numbers ie ISSN
            for key in self.issn_to_rating:
                if key == journal:
                    return self.issn_to_rating[key]
            return "no match"

        elif 65 <= ascii_code <= 90 or 97 <= ascii_code <= 122: #for letters ie journal name
            for key in self.name_to_rating:
                if key == journal:
                    return self.name_to_rating[key]
            return "no match"

        # Invalid format
        else:
            return "Unrecognized input format"
