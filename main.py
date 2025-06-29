from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.controller.SearchController import router as search_router

app = FastAPI()

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

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
