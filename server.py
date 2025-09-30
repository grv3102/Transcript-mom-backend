import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from services.ai_service import AIService
from services.doc_service import generate_doc
from services.pdf_service import generate_pdf

app = FastAPI()

# Initialize AI service
ai_service = AIService()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/ai-minutes")
async def ai_minutes(payload: dict = Body(...)):
    transcript = payload.get("transcript", "")
    structured = await ai_service.process_transcript(transcript)
    return structured

@app.get("/api/health")
async def health_check():
    return ai_service.health_check()

@app.post("/api/generate-doc")
async def generate_docx(data: dict = Body(...)):
    buf = generate_doc(data)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=minutes.docx"},
    )

@app.post("/api/generate-pdf")
async def generate_pdfx(data: dict = Body(...)):
    buf = generate_pdf(data)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=minutes.pdf"},
    )

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
