# VERIFYD — AI Influencer Compliance Platform

[![CI Pipeline](https://github.com/omkarpraval/AI-Compliance-Creators-Companies-/actions/workflows/ci.yml/badge.svg)](https://github.com/omkarpraval/AI-Compliance-Creators-Companies-/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google Gemini 2.0](https://img.shields.io/badge/Google_Gemini-2.0_Flash-8E75B2?style=flat&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.4+-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

VERIFYD is an enterprise-grade AI compliance verification platform that cross-references influencer contracts against delivered video assets to generate multi-modal audit trails, clause-by-clause verifications, evidence timelines, and automated compliance scoring.

---

## 🏛️ System Architecture

```mermaid
graph TB
    subgraph ClientLayer ["Client Layer (React 19 + TypeScript + Vite)"]
        CompanyPortal["Company / Brand Portal<br/>• Campaign Studio<br/>• Contract Review (Split PDF)<br/>• Submission Verification"]
        CreatorPortal["Creator Portal<br/>• Pre-flight Check<br/>• Submission Pipeline<br/>• Public Creator ID"]
        AdminPortal["Platform Admin<br/>• Aggregate Metrics<br/>• LLM Cost / Spend Audit<br/>• Job Queue Health"]
    end

    subgraph APILayer ["API Application Layer (FastAPI + Python 3.13)"]
        AuthRouter["Auth & Session Management<br/>(JWT + HttpOnly Cookies)"]
        ContractRouter["Contract Engine & Ingestion<br/>(PDFPlumber + Rapidfuzz)"]
        SubmissionRouter["Submission & Media Router<br/>(Presigned Uploads + Jobs)"]
        ReviewRouter["Review & Override System<br/>(Audit Trail Log)"]
        AdminRouter["Metrics & Governance<br/>(JSONB Aggregations)"]
    end

    subgraph IngestionAI ["AI Orchestration & Ingestion Pipeline"]
        PDFService["PDF Ingestion Service<br/>• Magic byte & size check<br/>• Word Bounding Box Normalizer (0-1)<br/>• SHA-256 Deduplication Cache"]
        FuzzyMatcher["Clause Bounding Box Resolver<br/>(Rapidfuzz Sliding Window ≥ 88%)"]
        GeminiClient["Hosted AI Services<br/>• Gemini 2.0 Flash (Clause Extraction)<br/>• Gemini Vision (Scanned Fallback)<br/>• Gemini Multi-modal (Video Compliance)"]
        ScoringEngine["Deterministic Scoring Engine<br/>• Critical failure gates<br/>• Arithmetic weights (0-100)<br/>• Duration & phrase post-checkers"]
    end

    subgraph DataLayer ["Data & Storage Layer"]
        PG["PostgreSQL 16 Engine<br/>• asyncpg (Runtime Pool)<br/>• psycopg (Sync Migrations)<br/>• CITEXT, JSONB, ARRAY, UUID"]
        PDFCache["PDF Extractions Cache<br/>(Content Hash SHA-256)"]
        Storage["Object Storage<br/>(Contracts, Videos, Evidence Frames)"]
    end

    ClientLayer -->|REST / JSON API| APILayer
    APILayer -->|Async Queries & JSONB Ops| PG
    APILayer -->|Extract & Normalize| PDFService
    PDFService -->|Cache Check / Store| PDFCache
    PDFService -->|Text Tokens & Prompts| GeminiClient
    GeminiClient -->|Raw Clauses| FuzzyMatcher
    FuzzyMatcher -->|source_bbox & source_page| PG
    SubmissionRouter -->|Video Verification Request| GeminiClient
    GeminiClient -->|Observations & Spans| ScoringEngine
    ScoringEngine -->|Verdicts & Evidence Items| PG
```

---

## 🔬 In-Depth Data & Verification Pipelines

### 1. Server-Side PDF Text Extraction & Clause Coordinate Matching (Task A)

```mermaid
flowchart TD
    A([User Uploads Contract PDF]) --> B[Compute SHA-256 Content Hash]
    B --> C{Cache Hit in<br/>pdf_extractions?}
    
    C -- Yes --> D[Load Cached Pages & Word Coordinates]
    C -- No --> E[Validate Magic Bytes %PDF- & Page Count ≤ 50]
    
    E --> F[Check Encryption with pypdf]
    F -- Password Protected --> F1[Raise ValidationError: PDF_ENCRYPTED]
    F -- Clean --> G[Extract with pdfplumber]
    
    G --> H[Extract Text & Word-level Bounding Boxes]
    H --> I[Normalize Coordinates 0.0 - 1.0 against Page W x H]
    
    I --> J{Has Usable Text Layer?<br/>non-ws chars > 40 per page}
    J -- No --> K[Set is_scanned = True<br/>Route inline PDF to Gemini Vision OCR]
    J -- Yes --> L[Join Page Text with Boundary Markers<br/>--- page N ---]
    
    K --> M[Save to pdf_extractions Cache Table]
    L --> M
    M --> D
    
    D --> N[Send Formatted Text to Gemini Clause Extractor v2]
    N --> O[Receive Structured Clauses with Verbatim source_text]
    
    O --> P[Rapidfuzz Sliding Window Matcher]
    P --> Q{Fuzzy Similarity<br/>Score ≥ 88%?}
    Q -- Yes --> R[Compute Union Bounding Box<br/>source_bbox & source_page]
    Q -- No --> S[Set source_bbox = NULL<br/>Fallback to No-Highlight Gracefully]
    
    R --> T[(Persist Clauses to PostgreSQL)]
    S --> T
    
    T --> U([Interactive React Split-View Contract Review])
```

---

### 2. Multi-Modal Submission Verification & Scoring Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Creator as Creator / Agency
    participant Web as Web Frontend (React)
    participant API as FastAPI Backend
    participant Worker as Pipeline Worker
    participant Gemini as Google Gemini 2.0 Flash
    participant DB as PostgreSQL 16 (JSONB)

    Creator->>Web: Upload Video Submission (Pre-flight or Final)
    Web->>API: POST /api/v1/submissions (video_key, caption, platform_url)
    API->>DB: Create Submission (status='queued')
    API->>Worker: Trigger score_submission job
    
    Worker->>DB: Fetch Governing Contract & Active Clauses
    Worker->>Gemini: Stream Video + Audio + Metadata + Structured Clause Schema
    Note over Gemini: Analyzes spoken audio, on-screen text (OCR),<br/>visual presence, competitor brands, disclosures (#ad)
    Gemini-->>Worker: Return Model Findings (Spans, Timestamps, Bounding Boxes, Confidence)
    
    Worker->>Worker: Run Deterministic Post-Verification Logic
    Note over Worker: • Math: 100 - (failed_crit * 100) - (failed_std * 15)<br/>• Override durations if timestamp math mismatches<br/>• Validate #ad tag presence in caption / OCR
    
    Worker->>DB: Write ComplianceReport (overall_score, verdict)
    Worker->>DB: Write ClauseVerdicts + EvidenceItems (start_ms, end_ms, payload JSONB)
    Worker->>DB: Update Submission status='report_ready'
    
    Web->>API: GET /api/v1/submissions/{id}
    API->>DB: Query submission with joined report & evidence
    DB-->>API: Full Compliance Audit Payload
    API-->>Web: Render Evidence Timeline & Synchronized Video Player
```

---

## 🗄️ Database Entity-Relationship Architecture (PostgreSQL 16)

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ USERS : "has members"
    ORGANIZATIONS ||--o{ CAMPAIGNS : "owns"
    USERS ||--o| CREATOR_PROFILES : "owns profile"
    CAMPAIGNS ||--o{ CONTRACTS : "governs"
    CREATOR_PROFILES ||--o{ CONTRACTS : "assigned to"
    CONTRACTS ||--o{ CLAUSES : "contains"
    CONTRACTS ||--o{ SUBMISSIONS : "delivers against"
    CONTRACTS ||--o| CONTRACTS : "supersedes (versioning)"
    SUBMISSIONS ||--o| COMPLIANCE_REPORTS : "evaluates"
    COMPLIANCE_REPORTS ||--o{ CLAUSE_VERDICTS : "contains"
    CLAUSE_VERDICTS ||--o{ EVIDENCE_ITEMS : "substantiated by"
    SUBMISSIONS ||--o{ JOBS : "executes"
    PDF_EXTRACTIONS ||--o{ CONTRACTS : "caches extraction for"

    ORGANIZATIONS {
        uuid id PK
        varchar name
        varchar org_type "brand | agency"
        jsonb settings
        timestamptz created_at
    }

    USERS {
        uuid id PK
        uuid org_id FK
        citext email "Unique, Case-Insensitive"
        varchar hashed_password
        varchar role "company_admin | creator | platform_admin"
        varchar full_name
        boolean is_active
        timestamptz last_login_at
    }

    CONTRACTS {
        uuid id PK
        uuid campaign_id FK
        uuid creator_id FK
        integer version
        uuid parent_contract_id FK
        varchar raw_document_key
        varchar source_content_hash FK
        varchar status "draft | needs_review | signed | superseded"
        numeric fee_amount "NUMERIC(12,2)"
        varchar fee_currency
    }

    PDF_EXTRACTIONS {
        varchar content_hash PK "SHA-256"
        integer page_count
        text full_text
        jsonb pages "ExtractedWord[] coordinates"
        boolean is_scanned
        varchar extraction_method
        integer char_count
        timestamptz created_at
    }

    CLAUSES {
        uuid id PK
        uuid contract_id FK
        varchar clause_ref "C-01, C-02"
        text source_text
        varchar clause_type
        jsonb params
        varchar modality "audio | visual | text_overlay | mixed"
        varchar severity "critical | standard | advisory"
        integer source_page
        jsonb source_bbox "Normalised bounding box union"
    }

    SUBMISSIONS {
        uuid id PK
        uuid contract_id FK
        integer contract_version
        uuid creator_id FK
        varchar kind "preflight | final"
        varchar video_file_key
        varchar status "report_ready | approved | changes_requested"
        integer attempt_number
    }

    COMPLIANCE_REPORTS {
        uuid id PK
        uuid submission_id FK
        integer overall_score "0-100"
        varchar verdict "pass | fail | needs_review"
        integer clauses_total
        integer clauses_passed
        integer clauses_failed
        numeric cost_estimate_usd "NUMERIC(12,4)"
        timestamptz generated_at
    }

    CLAUSE_VERDICTS {
        uuid id PK
        uuid report_id FK
        uuid clause_id FK
        varchar verdict "pass | fail | flagged"
        float confidence
        text rationale
        jsonb measured_value
        jsonb required_value
    }

    EVIDENCE_ITEMS {
        uuid id PK
        uuid verdict_id FK
        varchar evidence_type "transcript_span | visual_detection | ocr_text"
        integer start_ms
        integer end_ms
        float confidence
        jsonb payload "Text, Bounding Box, OCR tags"
    }
```

---

## 🚀 Prerequisites

1. **PostgreSQL 16+** (Required)
   - Extensions used: `citext`, `pg_trgm` (enabled automatically in migrations)
   - Connection string format: `postgresql+asyncpg://verifyd:verifyd@localhost:5432/verifyd`
2. **Python 3.11+ / 3.13**
3. **Node.js 20+ / npm 10+**
4. **Google Gemini API Key** (`GEMINI_API_KEY`)

---

## 🛠️ Quick Start

### 1. Database Setup (PostgreSQL)

You can run PostgreSQL locally or via Docker:

```bash
docker compose up -d db
```

Or ensure a local PostgreSQL server is running on port `5432` with database `verifyd` and user `verifyd` (password: `verifyd`).

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Ensure `DATABASE_URL` is set to:
```env
DATABASE_URL=postgresql+asyncpg://verifyd:verifyd@localhost:5432/verifyd
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Backend Setup & Migrations

From the root directory:

```bash
# Install backend in editable mode
pip install -e apps/api

# Run Alembic migrations against PostgreSQL
cd apps/api
python -m alembic upgrade head
cd ../..

# Seed demo data (7 users across brands, agencies, creators, with contracts & evidence)
python scripts/seed.py
```

### 4. Run the Backend API

```bash
python -m uvicorn verifyd.main:app --reload --port 8000 --app-dir apps/api/src
```

- API Interactive Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Readiness check: `http://localhost:8000/ready`

### 5. Frontend Setup & Run

```bash
cd apps/web
npm install
npm run dev
```

- Web App: `http://localhost:5173`

---

## 🧪 Automated Testing

Run the full pytest suite (including PDF extraction, PostgreSQL pagination stability, scoring arithmetic, and auth):

```bash
python -m pytest apps/api/tests -v
```

Build the frontend bundle:

```bash
cd apps/web
npm run build
```

---

## 🔑 Demo User Accounts

All accounts use the password: `Verifyd!2026`

| Role | Email | Description |
|---|---|---|
| **Brand Admin** | `admin@lumenskincare.com` | Lumen Skincare Company Administrator |
| **Brand Member** | `sarah@lumenskincare.com` | Lumen Skincare Team Member |
| **Agency Admin** | `admin@northlightmedia.com` | Northlight Media Agency Administrator |
| **Verified Creator** | `alex@creators.com` | Alex Rivers (`@alexrivers`) — Star demo with v1/v2 diffs |
| **Creator** | `maya@creators.com` | Maya Patel (`@mayaskin`) |
| **Creator** | `rohan@creators.com` | Rohan Sharma (`@rohancreates`) — Contract review demo |
| **Platform Admin** | `ops@verifyd.io` | Global Operations & Governance Reviewer |
