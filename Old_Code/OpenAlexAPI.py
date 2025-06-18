
import requests

base_url = "https://api.openalex.org/works"
params = {
    "search": "resilience pregnancy",
    "sort": "publication_year:desc",
    "per-page": 5  # maximal 200
}

response = requests.get(base_url, params=params)

if response.status_code == 200:
    data = response.json()
    for work in data['results']:
        print(f"Title: {work['title']}")
        print(f"Year: {work.get('publication_year', 'N/A')}")
        print(f"DOI: {work.get('doi', 'N/A')}")
        print(f"OpenAlex ID: {work['id']}")
        print("-" * 50)
else:
    print(f"Fehler: {response.status_code}")
