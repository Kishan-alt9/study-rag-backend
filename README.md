# study-rag-backend

## Project purpose

This repository is the backend for a new study-focused RAG project. It is separate
from the previous implementation; the frontend is planned for the separate
`study-rag-frontend` repository.

## Current status

**Initial scaffold only.** No application logic, PDF upload, RAG pipeline, search,
database integration, reranking, or LLM generation has been implemented.

## Planned high-level capabilities

The project may eventually support document ingestion and question answering over
study materials. The architecture and technologies for those capabilities are
proposals awaiting owner approval, not selected or implemented features. See
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
│       └── __init__.py
└── tests/
    └── .gitkeep
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

Python 3.13.7 has been verified for creating this project's virtual environment. Compatibility with future RAG dependencies has not yet been evaluated.

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


No runtime dependencies have been selected or installed yet. Dependency installation instructions will be added after the required libraries are chosen and their compatibility is checked.

### Tests

Automated tests have not been implemented yet. Testing instructions will be added as testable components are introduced.
