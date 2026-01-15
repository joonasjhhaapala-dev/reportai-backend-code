# ReportAI Backend

Python FastAPI backend for automated quality report generation with AI.

## Features

- 📤 **File Upload**: Excel (.xlsx, .xls) and CSV file support
- 🤖 **AI Analysis**: Claude API integration for intelligent data analysis
- 📊 **Multiple Formats**: Generate PDF, Word (DOCX), and Excel reports
- 🌍 **Multilingual**: Support for English and Finnish
- ⚡ **Fast**: Asynchronous processing with FastAPI

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **Anthropic Claude API** - AI-powered analysis
- **pandas** - Data manipulation and analysis
- **openpyxl** - Excel file handling
- **python-docx** - Word document generation
- **reportlab** - PDF generation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get your API key from: https://console.anthropic.com/

### 3. Run Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /
```
Returns server status.

### Upload File
```
POST /api/upload
```
Upload Excel or CSV file for analysis.

**Parameters:**
- `file` (multipart/form-data): File to upload

**Returns:**
```json
{
  "success": true,
  "file_id": "uploads/1234567890_data.xlsx",
  "filename": "data.xlsx",
  "size": 12345,
  "preview": {
    "rows": 100,
    "columns": 15,
    "column_names": ["col1", "col2", ...],
    "first_rows": [...],
    "sheets": ["Sheet1", "Sheet2"]
  }
}
```

### Analyze Data
```
POST /api/analyze
```
Analyze uploaded data with AI.

**Parameters:**
- `file_id` (form): File ID from upload response
- `template_type` (form): Report type (testing, quality, field, process)
- `language` (form): Language code (en, fi)

**Returns:**
```json
{
  "success": true,
  "analysis": {
    "executive_summary": "...",
    "key_findings": ["...", "..."],
    "statistical_analysis": "...",
    "recommendations": ["...", "..."],
    "conclusion": "..."
  }
}
```

### Generate Report
```
POST /api/generate
```
Generate final report in specified format.

**Parameters:**
- `file_id` (form): File ID from upload response
- `template_type` (form): Report type
- `report_title` (form): Report title
- `report_date` (form): Report date (YYYY-MM-DD)
- `company_name` (form): Company name (optional)
- `author_name` (form): Author name (optional)
- `output_format` (form): Output format (pdf, word, excel)
- `language` (form): Language code (en, fi)

**Returns:**
```json
{
  "success": true,
  "download_url": "/api/download/report_20250115.pdf",
  "filename": "report_20250115.pdf"
}
```

### Download Report
```
GET /api/download/{filename}
```
Download generated report file.

### Cleanup
```
DELETE /api/cleanup/{file_id}
```
Delete temporary files.

## Project Structure

```
report-backend/
├── main.py                 # FastAPI application
├── ai_analyzer.py          # Claude API integration
├── report_generator.py     # Report generation (PDF, Word, Excel)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── README.md              # This file
├── uploads/               # Temporary uploaded files
└── outputs/               # Generated reports
```

## Development

### Testing API

You can test the API using:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc
3. **curl**:

```bash
# Upload file
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@data.xlsx"

# Generate report
curl -X POST "http://localhost:8000/api/generate" \
  -F "file_id=uploads/1234_data.xlsx" \
  -F "template_type=testing" \
  -F "report_title=Test Report" \
  -F "report_date=2025-01-15" \
  -F "output_format=pdf" \
  -F "language=en"
```

## Deployment

### Option 1: Railway

1. Create account at [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard
4. Deploy automatically

### Option 2: Render

1. Create account at [Render.com](https://render.com)
2. Create new Web Service
3. Connect repository
4. Add environment variables
5. Deploy

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t reportai-backend .
docker run -p 8000:8000 --env-file .env reportai-backend
```

## Next Steps

1. ✅ Backend API working
2. 🔄 Update frontend to call backend API
3. 🔄 Add user authentication
4. 🔄 Add database for storing reports
5. 🔄 Add payment integration (Stripe)
6. 🔄 Deploy to production

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
