# de-ai MVP — Running locally

## Requirements
Python 3.11+.

```bash
git clone https://github.com/gaolei8888/de-ai.git
cd de-ai
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
uvicorn run:app --reload --port 8000
```

Open http://127.0.0.1:8000/ . API docs: http://127.0.0.1:8000/docs

Run tests from repository root:

```bash
python -m pytest -q
```

## Scope of first executable slice
- English/Chinese keyword-based text issue detection with exact offsets.
- HTML static inspection for missing img alt attributes, language, main landmark, and possible unlabeled inputs.
- Browser UI for submitting pasted source and reviewing evidence.
- All analysis in-memory; no uploads, tracking, database, external API or LLM calls.
- Audio/video inspection and source-code repair are **not yet implemented**.
- This is an early rule-based prototype, **not** a reliable AI-origin classifier, full accessibility audit, or production security analysis.

## Next increments
1. Robust HTML parsing and accessible-name computation, DOM state capture with Playwright in a sandbox.
2. Unified versioned Issue schema and benchmark/golden-set test fixtures.
3. Video shot detection + timestamped findings, and audio ASR/VAD analysis.
4. User approval, intent-guard checks, versioned repair operations.
5. Authentication, data isolation, rate limiting, and opt-in persistence before public deployment.
