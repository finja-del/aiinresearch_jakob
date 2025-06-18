import os
import clarivate.wos_starter.client
from clarivate.wos_starter.client import ApiClient, Configuration
from clarivate.wos_starter.client.api.documents_api import DocumentsApi
from clarivate.wos_starter.client.rest import ApiException
from pprint import pprint

# 1️⃣ API-Key richtig setzen
os.environ["API_KEY"] = "34fb3dd31f0621e066a60689e5f8f8e5c2158c78"
configuration = Configuration(host="https://api.clarivate.com/apis/wos-starter/v1")
configuration.api_key['ClarivateApiKeyAuth'] = os.environ["API_KEY"]

# 2️⃣ Mit API-Client verbinden
with ApiClient(configuration) as api_client:
    api_instance = DocumentsApi(api_client)
    
    # 3️⃣ Allgemeine Test-Query (erwartet Treffer)
    q_simple = 'TS=machine learning'
    try:
        response_simple = api_instance.documents_get(q=q_simple, db='WOS', limit=5, page=1)
    except ApiException as e:
        print("Fehler bei einfacher Abfrage:", e)
        raise SystemExit

    print("=== Einfache Query: 'TS=machine learning' ===")
    print("  Seite:", response_simple.metadata.page)
    print("  Limit:", response_simple.metadata.limit)
    print("  Total:", response_simple.metadata.total)
    print("  Hits-Zahl:", len(response_simple.hits))
    if response_simple.hits:
        for doc in response_simple.hits:
            print("  •", doc.title, "| UT:", doc.ut)  # UT = Unique Title‐Identifier
    else:
        print("  ⚠️ Keine Ergebnisse gefunden - evtl. Problem mit Key/Plan")

    # 4️⃣ Spezifische Query: Publikationsjahr 2024
    q_year = 'PY=2024'
    try:
        response_year = api_instance.documents_get(q=q_year, db='WOS', limit=5, page=1)
    except ApiException as e:
        print("Fehler bei Jahres-Abfrage:", e)
        raise SystemExit

    print("\n=== Spezifische Query: 'PY=2024' ===")
    print("  Seite:", response_year.metadata.page)
    print("  Limit:", response_year.metadata.limit)
    print("  Total:", response_year.metadata.total)
    if response_year.hits:
        print("  Beispiel-Dokument:", response_year.hits[0].title, "| UT:", response_year.hits[0].ut)
    else:
        print("  ⚠️ Keine Treffer für PY=2024. Möglicherweise noch keine 2024er Einträge oder Query zu eng.")