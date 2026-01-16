"""
ReportAI Backend API
FastAPI application for automated quality report generation
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd

# Import custom modules
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator

# Initialize FastAPI app
app = FastAPI(
    title="ReportAI API",
    description="Automated quality report generation with AI",
    version="1.0.0"
)

# CORS configuration - CRITICAL for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://reportai-frontend-production.up.railway.app",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files for downloads
app.mount("/downloads", StaticFiles(directory=str(OUTPUT_DIR)), name="downloads")

# Initialize AI analyzer and report generator
ai_analyzer = AIAnalyzer()
report_generator = ReportGenerator()

# In-memory storage for file metadata
file_store = {}


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "ReportAI Backend",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_analyzer": "active",
            "report_generator": "active"
        }
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process data file (Excel or CSV)
    Returns file ID and preview of data
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload Excel (.xlsx, .xls) or CSV file"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read and preview data
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=None)
            # If multiple sheets, use first sheet
            if isinstance(df, dict):
                sheet_names = list(df.keys())
                df = df[sheet_names[0]]
            else:
                sheet_names = ["Sheet1"]
        
        # Create preview
        preview = {
            "sheets": sheet_names if file.filename.endswith(('.xlsx', '.xls')) else ["Data"],
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "first_rows": df.head(5).to_dict('records')
        }
        
        # Store file metadata
        file_store[file_id] = {
            "filename": file.filename,
            "filepath": str(file_path),
            "uploaded_at": datetime.now().isoformat(),
            "preview": preview
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "preview": preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/generate")
async def generate_report(
    file_id: str = Form(...),
    template_type: str = Form("testing"),
    report_title: str = Form("Quality Report"),
    report_date: str = Form(None),
    company_name: str = Form(""),
    author_name: str = Form(""),
    output_format: str = Form("pdf"),
    language: str = Form("en")
):
    """
    Generate report from uploaded data
    """
    try:
        # Validate file_id
        if file_id not in file_store:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = file_store[file_id]
        file_path = file_info["filepath"]
        
        # Read data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Prepare data summary for AI analysis
        data_summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "sample_data": df.head(10).to_dict('records'),
            "statistics": df.describe().to_dict() if len(df) > 0 else {}
        }
        
        # Get AI analysis
        analysis = ai_analyzer.analyze_data(
            data_summary=data_summary,
            template_type=template_type,
            language=language
        )
        
        # Prepare report data
        report_data = {
            "title": report_title,
            "date": report_date or datetime.now().strftime("%Y-%m-%d"),
            "company": company_name,
            "author": author_name,
            "template_type": template_type,
            "language": language,
            "data_summary": data_summary,
            "analysis": analysis
        }
        
        # Generate report
        output_filename = f"report_{file_id}.{output_format}"
        output_path = OUTPUT_DIR / output_filename
        
        if output_format == "pdf":
            report_generator.generate_pdf(report_data, str(output_path))
        elif output_format == "word":
            report_generator.generate_docx(report_data, str(output_path))
        elif output_format == "excel":
            report_generator.generate_xlsx(report_data, str(output_path))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {output_format}")
        
        return {
            "success": True,
            "filename": output_filename,
            "download_url": f"/downloads/{output_filename}",
            "format": output_format
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.delete("/api/cleanup/{file_id}")
async def cleanup_files(file_id: str):
    """Clean up uploaded file and generated reports"""
    try:
        if file_id in file_store:
            # Remove uploaded file
            file_path = Path(file_store[file_id]["filepath"])
            if file_path.exists():
                file_path.unlink()
            
            # Remove from store
            del file_store[file_id]
            
            return {"success": True, "message": "Files cleaned up"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
