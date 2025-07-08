import json

class JournalFilter:
    def __init__(self):
        self.journals = []
        self._ranking_systems_order = {
            "ABDC": {
                "A*": 5, "A": 4, "B": 3, "C": 2, "no match": 0
            },
            "VHB": {
                "A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "no match": 0
            }
        }

    def _get_rank_value(self, ranking: str, system: str) -> int:
        system_ranks = self._ranking_systems_order.get(system.upper())
        if system_ranks:
            return system_ranks.get(ranking.strip().upper(), 0)
        return 0

    def load_journals_from_json(self, json_data_string: str) -> bool:
        try:
            parsed_data = json.loads(json_data_string)
            if not isinstance(parsed_data, list):
                return False
            validated_journals = []
            for item in parsed_data:
                if not isinstance(item, dict):
                    continue
                if "name" not in item or "ranking" not in item or "system" not in item:
                    continue
                validated_journals.append(item)
            self.journals = validated_journals
            return True
        except json.JSONDecodeError:
            return False
        except Exception:
            return False

    def filter_by_ranking(self, desired_ranking: str, system: str) -> list:
        if not self.journals:
            return []
        if not isinstance(desired_ranking, str) or not desired_ranking.strip():
            return []
        if not isinstance(system, str) or not system.strip():
            return []

        target_ranking_upper = desired_ranking.strip().upper()
        
        if target_ranking_upper == "no match":
            return []

        target_system_upper = system.strip().upper()

        filtered_results = []
        for journal in self.journals:
            if ('ranking' in journal and isinstance(journal['ranking'], str) and
                'system' in journal and isinstance(journal['system'], str)):
                
                if (journal['ranking'].strip().upper() == target_ranking_upper and
                    journal['system'].strip().upper() == target_system_upper):
                    filtered_results.append(journal)
        
        return filtered_results
