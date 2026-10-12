# Decision Log

This log records project decisions in chronological order. Confirmed decisions and
proposals are labeled separately. A proposal is not an approval or an implementation.
Existing entries must not be silently rewritten; record a reversal as a new entry and
retain the earlier history.

## 1. Project objective

Build a new study-focused RAG backend incrementally, with each major architectural
change explained, understood, and verified before implementation. This repository
starts as documentation and project scaffolding only; it does not contain a RAG
pipeline.

## 2. Development principles

- Develop in small, testable phases.
- Before a major architectural change, the tutor explains the concepts and
  alternatives, quizzes the student, and requires a passing result before
  implementation.
- Document every meaningful decision, implementation change, mistake, fix, and
  verification result.
- Keep confirmed decisions distinct from proposals awaiting approval.
- Preserve decision history. Record reversals and their lessons rather than silently
  rewriting prior decisions.
- `decisions.md` records the history of decisions; `flow.md` records the actual
  system flow and clearly separates it from proposals.
- Do not claim that a component exists until code and tests verify it.

## 3. Confirmed decisions

The following decisions were supplied and confirmed by the project owner:

| ID | Date | Decision |
| --- | --- | --- |
| D-001 | 2026-10-10 | This is a new RAG project, separate from the previous implementation. |
| D-002 | 2026-10-10 | The backend and frontend will live in separate GitHub repositories. |
| D-003 | 2026-10-10 | The backend repository is named `study-rag-backend`. |
| D-004 | 2026-10-10 | The frontend repository is named `study-rag-frontend`. |
| D-005 | 2026-10-10 | GitHub is the remote repository; development happens locally. |
| D-006 | 2026-10-10 | The project will be developed in small, testable phases. |
| D-007 | 2026-10-10 | Before every major architectural change, the tutor will explain the concepts and alternatives, quiz the student, and require a passing result before implementation. |
| D-008 | 2026-10-10 | Every meaningful decision, implementation change, mistake, fix, and verification result must be documented. |
| D-009 | 2026-10-10 | `decisions.md` records decision history; `flow.md` records the actual system flow. |
| D-010 | 2026-10-10 | Existing decisions must not be silently rewritten. Reversed decisions must retain their history. |

## 4. Proposed decisions awaiting approval

None of the following proposals is approved, finally selected, or implemented:

| ID | Date | Status | Proposal |
| --- | --- | --- | --- |
| P-001 | 2026-10-10 | Proposed — awaiting approval | Use a Python backend with a `src` layout. |
| P-002 | 2026-10-10 | Proposed — awaiting approval | Use PostgreSQL for document metadata and persistence. |
| P-003 | 2026-10-10 | Proposed — awaiting approval | Use a vector index for semantic retrieval. |
| P-004 | 2026-10-10 | Proposed — awaiting approval | Use lexical search for keyword retrieval. |
| P-005 | 2026-10-10 | Proposed — awaiting approval | Use hybrid retrieval with Reciprocal Rank Fusion (RRF). |
| P-006 | 2026-10-10 | Proposed — awaiting approval | Use a reranker to order retrieved passages. |
| P-007 | 2026-10-10 | Proposed — awaiting approval | Use an LLM for grounded answer generation. |
| P-008 | 2026-10-10 | Proposed — awaiting approval | Use OCR for scanned documents. |
| P-009 | 2026-10-10 | Proposed — awaiting approval | Use FastAPI to serve the backend. |

## 5. Mistakes, root causes and fixes

No project-specific mistakes, root causes, or fixes have been verified for this new
repository. Do not infer or invent incidents from the existence of a previous
implementation. Use the incident template below when a future mistake and its fix
are established.

## 6. Reversed decisions and lessons learned

No decisions have been reversed in this repository. When a decision is reversed,
retain its original entry and add a new dated entry describing the replacement and
the lesson learned.

## 7. Decision-log entry template

Copy this template for each future decision, implementation change, incident, or
verification record. Mark the status clearly as confirmed, proposed, rejected,
implemented, or reversed as appropriate.

### [Decision ID] — [Short title]

- **Date:**
- **Status:**
- **Context/problem:**
- **Decision:**
- **Reasoning:**
- **Alternatives considered:**
- **Trade-offs:**
- **Quiz outcome, if applicable:**
- **Implementation changes:**
- **Tests and verification:**
- **Follow-up actions:**



## Environment Setup

- **Date:** 2026-10-10
- **Status:** Implemented and verified
- **Decision:** Create the project's virtual environment in the repository root using Python's built-in `venv` module.
- **Location:** `.venv/`
- **Python version:** 3.13.7
- **Reasoning:** Isolate project dependencies from other Python projects and make the development environment reproducible.
- **Git:** `.venv` is ignored by `.gitignore`.

| D-007 | 2026-10-10 | Before every major architectural change, the tutor will explain the concepts and alternatives, quiz the student, and require a passing result before implementation. |

- **Verification:** Confirmed the environment's Python executable, version, and Git ignore rule.
- **Follow-up:** Check compatibility before choosing RAG libraries and dependencies.

### D-011 — Basic RAG v1 conceptual architecture

- **Date:** 2026-10-10
- **Status:** Approved — conceptual pipeline
- **Context/problem:** Establish the basic pipeline scope before implementing it in small, verified milestones.
- **Decision:** Basic RAG v1 consists of seven pipeline components:
  1. Select or receive study documents.
  2. Extract text from PDF pages.
  3. Split extracted text into chunks.
  4. Generate embeddings for chunks.
  5. Store and index the embedded chunks.
  6. Retrieve relevant chunks for a question.
  7. Generate a grounded answer with source references.
- **Reasoning:** Agree on the responsibilities in the pipeline while leaving implementation details open for compatibility checks.
- **Alternatives considered:** Not recorded.
- **Trade-offs:** Conceptual approval does not select libraries or mean that future pipeline stages have been implemented.
- **Quiz outcome:** The owner passed the architecture quiz with 4/4 answers.
- **Implementation changes:** None under this architecture approval alone.
- **Tests and verification:** Not applicable to the conceptual approval.
- **Technology status:** Proposed technology choices remain pending compatibility verification against the project's Python 3.13.7 environment. Existing P-001–P-009 entries remain proposals; they have not been silently changed or promoted to technology decisions.
- **Follow-up actions:** Verify each technology candidate before adding it as a dependency or implementing a later stage.

### D-012 — Milestone 1 PDF text reader

- **Date:** 2026-10-10
- **Status:** Implemented and verified
- **Context/problem:** Add the first testable pipeline component without implementing later RAG stages.
- **Decision:** Add a small `extract_pdf_pages(pdf_path)` reader that returns one `{source, page, text}` record per PDF page, keeps blank pages, and reports invalid inputs and unreadable/password-protected PDFs with clear exceptions.
- **Reasoning:** Per-page records retain source and page information needed by later steps while keeping this milestone independent of chunking, search, and generation.
- **Alternatives considered:** OCR and broader document-processing frameworks were excluded from this milestone.
- **Trade-offs:** Image-only PDF pages do not produce OCR text; encrypted PDFs requiring a password are rejected because this reader accepts no password.
- **Implementation changes:** Added `src/study_rag/pdf_reader.py` and `tests/test_pdf_reader.py`. Declared `PyMuPDF>=1.28.2` in `pyproject.toml` and installed PyMuPDF 1.28.2 into `.venv`. Compatibility was checked before installation: PyMuPDF 1.28.2 declares Python `>=3.10` and publishes a Windows x64 `cp310-abi3` wheel, compatible with the project's CPython 3.13.7 environment.
- **Tests and verification:** Ran `$env:PYTHONPATH = 'src'; .\.venv\Scripts\python.exe -m unittest discover -s tests -v` — 7 tests passed, 0 failed. Tests cover multiple pages and their order, source name and one-based numbering, an empty page, missing path, directory input, corrupt PDF, and an encrypted PDF requiring a password.
- **Follow-up actions:** Verify compatibility before adding dependencies for any later pipeline component.
