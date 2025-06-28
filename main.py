from flask import Flask, send_from_directory
import os
from backend.controller.SearchController import search_blueprint, SearchController

app = Flask(
    __name__,
    static_folder="frontend/static",
    template_folder="frontend"
)
app.register_blueprint(search_blueprint)


@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/search")
def search():
    return send_from_directory("frontend", "search.html")

# #ggf löschen nach merge
# # Set Filters
# filters = FilterCriteria()   #Filterkriterien initialisieren
# searchterm = "artificial intelligence"  # Beispiel Suchbegriff


# controller = SearchController()

# paper_list = controller.searchPapers(searchterm, filters)

# print(json.dumps([paper.__dict__ for paper in paper_list], indent=2))

if __name__ == "__main__":
    # # ✅ Local testing code: only runs when `main.py` is executed directly
    # print("Running startup test query...")
    # controller = SearchController()
    # query = "AI"
    # result = controller.searchPapers(query)
    # print("Test result:", result)

    # Optional: Run Flask web server
    app.run(debug=True)




    

