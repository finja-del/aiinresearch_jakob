from controller.SearchController import SearchController #neu Finja
from models.Ranking import Ranking #neu Finja

# Initialisierung des Controllers
controller = SearchController() #neu Finja

# Deine Suchanfrage
query = "AI"

# Starte die Suche
print(controller.searchPapers(query))

print ('hello world') #neu Finja
