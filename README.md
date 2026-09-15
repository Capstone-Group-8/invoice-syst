# Invoice Processing System - Capstone Group 8

This project addresses the time and errors involved in manually processing workplace invoices. The Alpha combines a React interface, FastAPI backend, database layer, validation logic, and an EasyOCR-based invoice extraction component while keeping a human in the loop.

## Team Roles

- Sally Little - Lead Architect
- Seth Roth - Interface Designer
- Andres Ortiz Sanchez - Integration Lead

## Alpha Architecture

`React frontend -> FastAPI -> database / validation`

The OCR module uses EasyOCR to extract invoice text. OCR parsing and full end-to-end persistence are active integration work for the Alpha release.

## Quick Start (local Alpha)

### 1. Backend

```bash
py -m pip install -r requirements.txt
py seed_demo.py
py -m uvicorn main:app --reload --port 8001
```

Open API documentation at `http://127.0.0.1:8001/docs`.

The default database is local SQLite so the Alpha can run without XAMPP. To use MySQL, copy `.env.example` values into your environment and set `DATABASE_URL` to the team MySQL connection string.

### 2. Frontend

```bash
cd frontend
npm install
```

Copy `frontend/.env.example` to `frontend/.env`, then run:

```bash
npm run dev
```

Open `http://localhost:5173`.

## Tests

```bash
pytest -q
```

Frontend build check:

```bash
cd frontend
npm run build
```

GitHub Actions runs the backend tests and frontend build on pull requests to `main`.

## AI / OCR Module

The repository contains an EasyOCR/PyMuPDF extraction module under `Invoice Extraction/`. It demonstrates AI-assisted text extraction from invoice PDFs. The team is integrating OCR output with validation, structured invoice fields, and the human review interface.

## Alpha Limitations / Technical Debt

- OCR-to-database persistence is still being integrated.
- Current parsing is most developed for the available Bullseye invoice samples.
- Broader vendor-format support is a post-MVP/stretch goal.
- Production deployment/security hardening remains future work.
