# Medical Pipeline

Minimal runnable scaffold for a medical document parsing pipeline. The current
implementation keeps everything lightweight so you can run it without external
dependencies like PostgreSQL or heavyweight PDF libraries.

## Quick start
1. Create a virtual env (optional) and install deps:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the demo pipeline:
   ```bash
   python -m src.main
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Where to extend
- `src/services/pdf_parser.py`: replace the line-based parser with a real PDF/EMR parser.
- `src/services/data_processor.py`: add normalization, NLP, and validation steps.
- `src/services/db_repository.py` + `src/database/connection.py`: connect to Postgres and use the schema in `src/database/schema.sql`.

## Environment
- `.env` is provided for future database/API keys; it is not loaded automatically in code yet.
