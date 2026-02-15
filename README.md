# Event Poster Extraction MVP

A hybrid OCR/Vision system that intelligently extracts structured event data from poster images using FastAPI and Next.js.

## Features

- **Intelligent Routing**: Automatically chooses between OCR-first (fast, cheap) or Vision (accurate) routes based on image complexity
- **Fallback Mechanism**: Automatically retries with Vision if OCR extraction is insufficient
- **Multiple LLM Providers**: Supports Mock (testing), OpenAI (GPT-4o), and Anthropic (Claude 3.5 Sonnet)
- **Data Normalization**: Standardizes dates, times, phone numbers, and emails
- **Dynamic Form Rendering**: Auto-generates editable forms from extracted data
- **Export Functionality**: Download as JSON or copy to clipboard

## Architecture

```
event-poster-extraction/
├── backend/          # FastAPI Python application
│   ├── app/
│   │   ├── core/            # Pipeline orchestration
│   │   ├── preprocessing/   # Image processing & complexity scoring
│   │   ├── extractors/      # PaddleOCR integration
│   │   ├── llm/             # LLM adapters (Mock, OpenAI, Anthropic)
│   │   ├── postprocessing/  # Normalization & validation
│   │   └── api/v1/endpoints/# FastAPI routes
│   └── tests/
└── frontend/         # Next.js 15 App Router
    ├── app/              # Pages
    ├── components/       # React components
    └── lib/              # Types & utilities
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Web framework
- **OpenCV** - Image preprocessing
- **PaddleOCR** - OCR engine
- **OpenAI / Anthropic** - LLM providers
- **Pydantic** - Data validation

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **react-dropzone** - File upload
- **lucide-react** - Icons

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows Git Bash
   # or
   source venv/bin/activate       # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Note: PaddleOCR models (~14MB) will auto-download to `~/.paddleocr/` on first run.

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` to set:
   - `LLM_PROVIDER`: `mock` (default, no API key needed), `openai`, or `anthropic`
   - `LLM_API_KEY`: Your API key (only if using OpenAI/Anthropic)
   - `LLM_MODEL`: Optional model override

5. **Run backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will start at [http://localhost:8000](http://localhost:8000)

   API Documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.local.example .env.local
   ```

   Default: `NEXT_PUBLIC_API_URL=http://localhost:8000`

4. **Run frontend**:
   ```bash
   npm run dev
   ```

   Frontend will start at [http://localhost:3000](http://localhost:3000)

## Usage

### 1. Start Both Services

**Terminal 1 - Backend**:
```bash
cd backend
source venv/Scripts/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### 2. Upload Event Poster

1. Open [http://localhost:3000](http://localhost:3000)
2. Drag-and-drop or click to upload an event poster (PNG, JPG, WEBP)
3. Wait for extraction (2-5 seconds)
4. Review extracted data in dynamic form
5. Edit fields if needed
6. Export as JSON

### 3. API Testing (Optional)

Test backend directly via Swagger UI:
- Open [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Try the `/api/v1/extract` endpoint

Or use curl:
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@poster.jpg"
```

## Configuration

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `mock` | LLM provider: `mock`, `openai`, `anthropic` |
| `LLM_API_KEY` | - | API key for OpenAI/Anthropic |
| `LLM_MODEL` | - | Model override (e.g., `gpt-4o`, `claude-3-5-sonnet-20241022`) |
| `OCR_DEFAULT_LANG` | `en` | OCR language code |
| `PREPROCESS_MAX_DIM` | `2000` | Max image dimension (pixels) |
| `BLUR_THRESHOLD` | `100.0` | Blur detection threshold |
| `COMPLEXITY_THRESHOLD` | `0.7` | Routing threshold (OCR vs Vision) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## How It Works

### Extraction Pipeline

1. **Image Upload** → User uploads poster via frontend
2. **Preprocessing** → Resize, grayscale, CLAHE, denoise (OpenCV)
3. **Complexity Scoring** → Calculate blur, edge density, text density
4. **Route Decision** →
   - **OCR-first** if clear and text-heavy
   - **Vision** if blurry or graphics-heavy
5. **Extraction**:
   - **OCR Route**: PaddleOCR → LLM post-processing
   - **Vision Route**: LLM vision analysis
6. **Fallback** → If OCR missing critical fields, retry with Vision
7. **Normalization** → Standardize dates, times, phone numbers, emails
8. **Validation** → Check critical fields, calculate confidence, add warnings
9. **Response** → Return structured JSON to frontend

### Complexity Routing Logic

```python
if is_blurry or overall_complexity > 0.7:
    → Vision route
elif text_density > 0.5 and not is_blurry:
    → OCR-first route
else:
    → Vision route (default)
```

### Output Schema

```json
{
  "type": "event_poster",
  "route": "ocr_first" | "vision" | "ocr_fallback_vision",
  "complexity_score": {
    "blur_variance": 150.5,
    "edge_density": 0.12,
    "text_density": 0.68,
    "overall_complexity": 0.45,
    "is_blurry": false
  },
  "confidence": 0.87,
  "fields": {
    "event_name": {"value": "...", "confidence": 0.95, "source": "line 1"},
    "date": {"value": "2026-03-15", "confidence": 0.90, "source": "line 2"},
    ...
  },
  "extra": [
    {"key": "wifi_available", "value": "Yes", "confidence": 0.70, "source": "line 12"}
  ],
  "warnings": [...]
}
```

## Testing

### Backend Unit Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Manual Testing

1. Use sample event posters (create simple text-heavy and complex graphic-heavy posters)
2. Test different routes:
   - Simple poster → Should use `ocr_first`
   - Complex poster → Should use `vision`
   - Force route: `force_route=ocr_first` or `force_route=vision`
3. Verify:
   - Correct fields extracted
   - Dates normalized to ISO 8601
   - Times normalized to 24h format
   - Confidence scores reasonable
   - Warnings for missing critical fields

## Deployment

### Backend (Railway/Render/AWS)

1. Set environment variables in platform
2. Ensure `requirements.txt` is up to date
3. Deploy with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)

1. Set `NEXT_PUBLIC_API_URL` to deployed backend URL
2. Deploy via Git integration or CLI
3. Ensure CORS origins in backend include frontend URL

## Troubleshooting

### PaddleOCR Installation Issues

If PaddleOCR fails to install:
```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddleocr
```

### CORS Errors

Ensure backend `.env` has:
```
CORS_ORIGINS=["http://localhost:3000", "your-frontend-url"]
```

### LLM API Errors

- For testing: Use `LLM_PROVIDER=mock` (no API key needed)
- For OpenAI: Set `LLM_API_KEY=sk-...` and `LLM_PROVIDER=openai`
- For Anthropic: Set `LLM_API_KEY=sk-ant-...` and `LLM_PROVIDER=anthropic`

## Future Enhancements

- [ ] Multi-language OCR support (beyond English)
- [ ] Batch processing (multiple posters)
- [ ] User feedback loop (correct extractions → improve model)
- [ ] Redis caching for OCR results
- [ ] Fine-tuned PaddleOCR on event poster dataset
- [ ] Database persistence (PostgreSQL/Supabase)

## License

MIT

## Contributors

Built with Claude Code as an MVP demonstration of hybrid OCR/Vision extraction.
