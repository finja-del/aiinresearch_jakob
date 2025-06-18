import requests

API_Key="4f8e6aded569f7273528997a3b055f35"

BaseUrl="https://api.elsevier.com/content/search/scopus"


params = {
    "query": "TITLE-ABS-KEY(The effect of taxes on the economy)",
    "apiKey": API_Key,
    "count": 5,
    "start": 0
}

headers = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_Key
}
response = requests.get(BaseUrl, headers=headers, params=params)
if response.status_code == 200:
    data = response.json()
    for entry in data.get("search-results", {}).get("entry", []):
        print("Titel:", entry.get("dc:title"))
    
        print("Autoren:", entry.get("dc:creator"))
        print("DOI:", entry.get("prism:doi"))
        print("Erscheinungsjahr:", entry.get("prism:coverDate"))
        print("Abstract:", entry.get("dc:description"))
        print("Link:", entry.get("link", [{}])[0].get("@href"))
        print("Affiliationen:", entry.get("affiliation", [{}])[0].get("affilname"))
        print("ISSN:", entry.get("prism:issn"))
        print("Scopus-ID:", entry.get("dc:identifier"))
        print("Cited by:", entry.get("citedby-count"))
        print("URL:", entry.get("link", [{}])[1].get("@href"))
        print("Jurnal:", entry.get("prism:publicationName"))
else:
    print("Fehler:", response.status_code)
    print(response.text)


