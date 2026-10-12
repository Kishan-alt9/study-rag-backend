# study-rag-backend

## Project purpose

This repository is the backend for a new study-focused RAG project. It is separate
from the previous implementation; the frontend is planned for the separate
`study-rag-frontend` repository.

## Current status

**Milestone 1 complete:** the backend can extract text page by page from a local
PDF. Upload handling, chunking, search, database integration, and answer generation
are not implemented.

## Planned high-level capabilities

The Basic RAG v1 pipeline has conceptual approval, but its later stages and their
technology choices remain pending compatibility checks and implementation. See
[`decisions.md`](./decisions.md) and [`flow.md`](./flow.md).

## Repository structure

```text
study-rag-backend/
├── decisions.md
├── flow.md
├── README.md
├── pyproject.toml
├── src/
│   └── study_rag/
│       ├── __init__.py
│       └── pdf_reader.py
└── tests/
    └── test_pdf_reader.py
```

The root `.gitignore` contains local-file exclusions and is not shown above.

## Development principles

- Work in small, testable phases.
- Before a major architectural change, explain concepts and alternatives, quiz the
  student, and require a passing result before implementing the change.
- Document meaningful decisions, implementation changes, mistakes, fixes, and
  verification results.
- Keep proposed architecture distinct from verified behavior.

The decision history is maintained in [`decisions.md`](./decisions.md). The actual
system flow and separately labeled future proposals are maintained in
[`flow.md`](./flow.md).


## Development Setup

### Prerequisites

- Python installed and accessible through the Windows `py` launcher.
- Git.
- Visual Studio Code (recommended).

Python 3.13.7 has been verified for this project's virtual environment. PyMuPDF's
compatibility has been checked for the PDF reader; other future dependencies have
not yet been evaluated.

### Create the Virtual Environment

From the backend repository root, open a PowerShell terminal and run:

```powershell
py -m venv .venv
```

### Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify the active Python interpreter:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

The executable should point to the project's `.venv` directory.

If PowerShell activation is blocked, use the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe --version
```

### Dependencies

PyMuPDF is used for page-level PDF text extraction. It is declared in
`pyproject.toml` and has been installed into `.venv` after checking compatibility
with Python 3.13.7.

### Tests

Run the unit tests from the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### PDF text reader

`extract_pdf_pages` returns one record for every PDF page, including blank pages.
Each record contains the PDF filename, a one-based page number, and extracted
text. For example:

```python
from study_rag.pdf_reader import extract_pdf_pages

pages = extract_pdf_pages("course-notes.pdf")
for page in pages:
    print(page["source"], page["page"], page["text"])
```

This reader does not perform OCR or modify the PDF. Missing files, directories,
corrupt or unreadable PDFs, and PDFs requiring a password raise documented errors.
