from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.controller.SearchController import router as search_router
from backend.controller.ExportController import router as export_router

app = FastAPI()
application = app  # 👈 Wichtig für AWS Beanstalk
#komentar zum pushen

# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# HTML routes (basic file responses)
@app.get("/")
async def home():
    return FileResponse("frontend/index.html")

@app.get("/search")
async def search():
    return FileResponse("frontend/search.html")

# Include search API routes
app.include_router(search_router, prefix="/api")
# Include export API routes
app.include_router(export_router, prefix="/api")


