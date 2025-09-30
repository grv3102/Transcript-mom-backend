import os
import uvicorn
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from services.ai_service import AIService
from services.doc_service import generate_doc
from services.pdf_service import generate_pdf

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Meeting Transcript Processor",
    description="Convert meeting transcripts into structured minutes using AI",
    version="2.0.0"
)

# Initialize AI service with error handling
try:
    ai_service = AIService()
except Exception as e:
    print(f"Warning: AI service initialization failed: {e}")
    ai_service = None

# CORS setup - updated for better performance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["Content-Type", "Authorization"],  # Specific headers
)

@app.post("/api/ai-minutes")
async def ai_minutes(payload: dict = Body(...)):
    """Process meeting transcript and return structured minutes"""
    try:
        transcript = payload.get("transcript", "")
        
        if not transcript or not transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript is required and cannot be empty")
        
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI service is not available")
        
        # Process transcript
        structured = await ai_service.process_transcript(transcript)
        return structured
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not ai_service:
        return {
            "status": "unhealthy",
            "error": "AI service not initialized",
            "timestamp": None
        }
    return ai_service.health_check()

@app.post("/api/generate-doc")
async def generate_docx(data: dict = Body(...)):
    """Generate DOCX document from structured meeting data"""
    try:
        if not data:
            raise HTTPException(status_code=400, detail="Meeting data is required")
        
        buf = generate_doc(data)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=meeting_minutes.docx"},
        )
        
    except Exception as e:
        print(f"Error generating DOCX: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate document: {str(e)}")

@app.post("/api/generate-pdf")
async def generate_pdfx(data: dict = Body(...)):
    """Generate PDF document from structured meeting data"""
    try:
        if not data:
            raise HTTPException(status_code=400, detail="Meeting data is required")
        
        buf = generate_pdf(data)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=meeting_minutes.pdf"},
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate document: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(
        "server:app", 
        host=host, 
        port=port, 
        reload=True,
        log_level="info",
        access_log=True
    )
