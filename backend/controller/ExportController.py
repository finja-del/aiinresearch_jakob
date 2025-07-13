from fastapi import APIRouter, HTTPException
from backend.models.PaperDTO import PaperDTO
from typing import List
import os
import csv
from datetime import datetime
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from io import StringIO

# Router definieren
router = APIRouter()

# Export-Verzeichnis definieren
EXPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)

@router.post("/download")
async def export_papers_endpoint(request: Request):
    data = await request.json()
    papers: List[PaperDTO] = [PaperDTO(**paper) for paper in data]
    
    # CSV in-memory generieren
    csv_buffer = StringIO()
    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=[
            'title', 'authors', 'abstract', 'date', 'source','sources','sourceCount', 'vhbRanking', 'abdcRanking', 
            'journal_name', 'issn', 'eissn', 'doi', 'url', 'citations', 'journal_quartile'
        ],
        delimiter=';'
    )
    writer.writeheader()
    for paper in papers:
        paper_dict = paper.to_api_dict()
        if isinstance(paper_dict['authors'], list):
            paper_dict['authors'] = ", ".join(paper_dict['authors'])
        writer.writerow(paper_dict)

    # StringIO auf den Anfang zurücksetzen
    csv_buffer.seek(0)

    # Response zurückgeben
    response = StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv"
    )
    # Dateiname im Download-Header setzen
    response.headers["Content-Disposition"] = "attachment; filename=papers_export.csv"
    return response

@router.post("/export")
async def export_papers_endpoint(request: Request):
     data = await request.json()
     controller = ExportController()
     papers: List[PaperDTO] = [PaperDTO(**paper) for paper in data]
     
     print("Erhaltene Daten:", data)
     filename = controller.export_papers_to_csv(papers)
     return {"status": "received"}
     
   # 
   # return {"message": "Export erfolgreich.", "filename": filename}

class ExportController:

    def __init__(self):
        self.export_path = EXPORT_DIR

    def export_papers_to_csv(self, papers: List[PaperDTO]) -> str:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"papers_export_{now}.csv"
        full_path = os.path.join(self.export_path, filename)

        # Header aus PaperDTO Feldern
        header = [
            'title', 'authors', 'abstract', 'date', 'source','sources','sourceCount', 'vhbRanking', 'abdcRanking', 
            'journal_name', 'issn', 'eissn', 'doi', 'url', 'citations', 'journal_quartile'
        ]

        with open(full_path, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header, delimiter=';')
            writer.writeheader()

            for paper in papers:
                # Konvertiere PaperDTO in API-Dict für Export
                paper_dict = paper.to_api_dict()

                # Autoren als Komma-getrennte Zeichenkette
                if isinstance(paper_dict['authors'], list):
                    paper_dict['authors'] = ", ".join(paper_dict['authors'])

                writer.writerow(paper_dict)

        print(f"✅ Export abgeschlossen: {full_path}")
        return filename