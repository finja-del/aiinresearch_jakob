from backend.controller.SearchController import SearchController
from backend.models.FilterCriteria import FilterCriteria
import json
from dataclasses import asdict

# Set Filters
filters = FilterCriteria()   #Filterkriterien initialisieren
searchterm = "artificial intelligence"  # Beispiel Suchbegriff


controller = SearchController()

paper_list = controller.searchPapers(searchterm, filters)

print(json.dumps([paper.__dict__ for paper in paper_list], indent=2))
