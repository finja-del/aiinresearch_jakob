from flask import Flask
from backend.controller.SearchController import search_blueprint, SearchController

app = Flask(__name__)
app.register_blueprint(search_blueprint)

if __name__ == "__main__":
    # Optional: Run Flask web server
    app.run(debug=True)

    # ✅ Local testing code: only runs when `main.py` is executed directly
    print("Running startup test query...")
    controller = SearchController()
    query = "AI"
    result = controller.searchPapers(query)
    print("Test result:", result)

