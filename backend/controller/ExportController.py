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
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import PatternFill
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font
from io import BytesIO
from fastapi import APIRouter, Request
from typing import List
from backend.models.PaperDTO import PaperDTO

# Router definieren
router = APIRouter()

# Export-Verzeichnis definieren
EXPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)



router = APIRouter()

@router.post("/download")
async def export_papers_as_xlsx(request: Request):
    data = await request.json()
    papers: List[PaperDTO] = [PaperDTO(**paper) for paper in data]

    # Neues Excel Workbook erstellen
    wb = Workbook()
    ws = wb.active
    ws.title = "Papers"

    # Spaltenüberschriften
    headers = [
        'title', 'authors', 'abstract', 'date', 'source','sources','source_count',
        'vhbRanking', 'abdcRanking', 'journal_name', 'issn', 'eissn',
        'doi', 'url', 'citations', 'journal_quartile'
    ]

    # Überschriften in fett
    header_font = Font(bold=True)
    ws.append(headers)
    for col in ws.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers)):
        for cell in col:
            cell.font = header_font
            cell.alignment = cell.alignment.copy(wrap_text=True)

    # Inhalte einfügen
    for paper in papers:
        paper_dict = paper.to_api_dict()
        row = [
            paper_dict.get("title", ""),
            ", ".join(paper_dict.get("authors", [])) if isinstance(paper_dict.get("authors"), list) else paper_dict.get("authors", ""),
            paper_dict.get("abstract", ""),
            paper_dict.get("date", ""),
            paper_dict.get("source", ""),
            ", ".join(paper_dict.get("sources", [])) if isinstance(paper_dict.get("sources"), list) else paper_dict.get("sources", ""),
            paper_dict.get("source_count", 0),
            paper_dict.get("vhbRanking", ""),
            paper_dict.get("abdcRanking", ""),
            paper_dict.get("journal_name", ""),
            paper_dict.get("issn", ""),
            paper_dict.get("eissn", ""),
            paper_dict.get("doi", ""),
            paper_dict.get("url", ""),
            paper_dict.get("citations", 0),
            paper_dict.get("journal_quartile", "")
        ]
        ws.append(row)
    end_row = ws.max_row
    end_col = ws.max_column
    table_range = f"A1:{ws.cell(row=end_row, column=end_col).coordinate}"

    excel_table = Table(displayName="PaperExport", ref=table_range)
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False
    )
    excel_table.tableStyleInfo = style
    ws.add_table(excel_table)
    # Spaltenbreiten automatisch anpassen (optional rudimentär)
    for col in ws.columns:
        max_length = max((len(str(cell.value)) for cell in col if cell.value), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)
    # Excel-Datei in BytesIO speichern
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=papers_export.xlsx"
        }
    )

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