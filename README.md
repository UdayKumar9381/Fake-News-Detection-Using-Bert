# Fake News Detection — Project Documentation

## Project Overview

This repository implements a BERT-based Fake News Detection system with a FastAPI backend, a React frontend, utilities for file text extraction and preprocessing, and training artifacts for the model. The system supports text classification, document/image uploads (PDF, DOCX, JPG/PNG), and source verification via news search APIs.

## Key Features
- **BERT-based classification:** Classifies input text as `Real` or `Fake` with confidence scores.
- **File upload & OCR:** Accepts PDFs, Word documents and images and extracts text using PyPDF2, python-docx and Tesseract OCR.
- **Source verification:** Searches Google News / NewsAPI and checks for trusted domain mentions to compute a credibility score.
- **REST API:** FastAPI endpoints for prediction, file upload, verification and health checks.
- **React frontend:** Vite + React UI to interact with the API.

## Repository Layout (important paths)
- `backend/` — Python backend and model files.
  - `backend/api/main.py` — FastAPI application and endpoints.
  - `backend/api/prediction.py` — BERT predictor implementation.
  - `backend/api/verification.py` — Source verification logic.
  - `backend/utils/` — `text_processing.py`, `file_extractor.py`, `config.py`.
- `frontend/` — React + Vite web client.
- `training/` — Training notebooks and scripts (Colab notebook, preprocessing, evaluation).
- `model/fake_news_bert_model/` — Trained model artifacts (tokenizer, config, weights).
- `datasets/` — raw and processed datasets used for training and evaluation.
- `docs/` — project docs and diagrams (this file added here).

## Quick Start — Local

Prerequisites:
- Python 3.9+ (venv recommended)
- Node.js + npm
- Tesseract OCR installed for image OCR

Backend (run from repository root):

```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
# Ensure model files exist at the path set in .env or default ./model/fake_news_bert_model
python -m api.main
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend in the browser (usually http://localhost:5173) and the API docs at `http://localhost:8000/docs`.

## Environment & Configuration

Primary configuration for backend is in `backend/.env`. Important variables:

- `MODEL_PATH` — path to the trained BERT model directory (default `./model/fake_news_bert_model`).
- `HOST` and `PORT` — server host and port (defaults `0.0.0.0:8000`).
- `GOOGLE_API_KEY`, `GOOGLE_CX` — Google Custom Search for news verification (optional).
- `NEWS_API_KEY` — NewsAPI key (optional).
- `MAX_FILE_SIZE` — upload max size in bytes (default 10485760 = 10MB).

Backend runtime settings are exposed through `backend/utils/config.py` via the `config` singleton.

## API Reference (summary)

Base host: `http://<HOST>:<PORT>` (defaults `http://0.0.0.0:8000`)

- GET `/` — Health/info; returns model and endpoints list.
- GET `/health` — Detailed health check (model + config summary).
- POST `/predict-text` — Predicts a single text input.
  - Request JSON: `{ "text": "<news text>" }`
  - Response: `{ "prediction": "Real|Fake", "label": 0|1, "confidence": <0-100>, ... }`
- POST `/upload-file` — Upload PDF/DOCX/JPG/PNG and run extraction + prediction.
  - Multipart file upload. Returns file metadata, `prediction`, `confidence`, and a text preview.
- POST `/verify-source` — Performs prediction and verification against Google News, NewsAPI and trusted domains.
  - Request JSON: `{ "text": "<news text>" }`
  - Response includes `source_verification`, `credibility_score`, `official_approval`, `verification_summary`.
- GET `/model-info` — Returns loaded model metadata (device, tokenizer vocab size, max length).

Note: full interactive docs are available at `/docs` (Swagger UI) when server runs.

## Model Details

- The predictor uses `transformers`' `BertTokenizer` and `BertForSequenceClassification` loaded from `MODEL_PATH`.
- The `FakeNewsPredictor` (in `backend/api/prediction.py`) handles text cleaning, tokenization, model inference and formatting of results.
- Prediction outputs include class probabilities, confidence percentage and a `confidence_level` derived from thresholds in `config.py`.

## Text Processing & File Extraction

- `backend/utils/text_processing.py` contains `clean_text()`, `validate_text()`, `truncate_text()` and simple `extract_keywords()`.
- `backend/utils/file_extractor.py` supports PDF, DOCX and image OCR (via `pytesseract`).

Supported file types: `.pdf`, `.docx`, `.doc`, `.jpg`, `.jpeg`, `.png`.

## Training & Evaluation

- Training notebook: `training/bert_training_colab.ipynb` (Colab-ready, GPU recommended).
- Preprocessing: `training/data_preprocessing.py`.
- Evaluation: `training/model_evaluation.py`; artifacts saved to `training/training_results/` including `metrics.json`, confusion matrix and training history.

## Dependencies

Backend highlights (see `backend/requirements.txt`):
- `fastapi`, `uvicorn`, `torch`, `transformers`, `PyPDF2`, `python-docx`, `pytesseract`, `Pillow`, `requests`, `beautifulsoup4`, `python-dotenv`

Frontend highlights (see `frontend/package.json`):
- `react`, `axios`, `vite`, `tailwindcss`

## Testing

- Unit / integration tests are under `tests/` (`test_api.py`, `test_model.py`). Run them using your preferred test runner (e.g., `pytest`).

## Deployment Notes

- For production, consider serving the API using a process manager (Gunicorn/Uvicorn workers) behind a reverse proxy (NGINX) and enabling HTTPS.
- Use GPU-enabled machines for inference if latency matters and the model is large.
- Ensure API keys for Google Custom Search / NewsAPI are configured in environment variables for full verification functionality.

## Troubleshooting & Common Issues

- "Model path does not exist" — make sure `MODEL_PATH` points to a directory containing tokenizer and model files (e.g., `config.json`, `pytorch_model.bin` / `model.safetensors`).
- OCR empty output — ensure Tesseract is installed and accessible in PATH.
- Slow inference — enable CUDA device and install appropriate `torch` binary for CUDA.

## Contributing

- Follow standard GitHub flow: fork, branch, PR.
- Run tests and linters before PR.

## License & Contact

- See `LICENSE` at repository root for license details.
- For questions, open an issue or contact the maintainers listed in the project repository.

---

Generated from repository READMEs and backend sources. If you want, I can:
- commit this file to a branch,
- expand the API reference with example requests/responses,
- or generate a concise developer quickstart checklist.
