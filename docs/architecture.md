# Utthan (उत्थान) — Architecture & Technical Specifications

> **Notice:** This document defines the architectural baseline for Phase 0 and the target specifications for future implementation phases. It explicitly differentiates between currently implemented components and planned/future components.

---

## 1. System Architecture Overview

### Current Implementation Baseline (Phase 1 Implemented)

```
┌─────────────────────────────────────────────────────────────┐
│                       Citizen Browser                       │
│           (Vite 8 + React 19 + Tailwind CSS 3.4)            │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               │ [PARTIAL] Web Speech API      │ [PARTIAL] Sarvam AI Bulbul:v3
               ▼ (Browser-native STT)          ▼ (Client-side Direct TTS)
┌─────────────────────────────────────────────────────────────┐
│                 src/services/aiService.js                   │
│        (Client-side direct integration with SaaS APIs)      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          PHASE 1 IMPLEMENTED DATA FOUNDATION LAYER          │
├─────────────────────────────────────────────────────────────┤
│ 1. Official Locations:  src/data/canonicalLocations.json    │
│    (Authoritative 36 States/UTs & 784 Districts from LGD)   │
│    Application Module:  src/data/locations.js (Derived)     │
│    Raw Source:          data/raw/lgd_districts.xls.xlsx     │
│                                                             │
│ 2. Verified Schemes:    src/data/verifiedOpportunities.js   │
│    (7 Real Government Schemes with NSQF & Source URLs)      │
│                                                             │
│ 3. Skills Catalog:      src/data/verifiedOpportunities.js   │
│    (11 Standardized Skills with SSC QP Codes)               │
│                                                             │
│ 4. Matching Engine:     src/services/recommendationEngine.js│
│    (Deterministic Hard Eligibility + Weighted 100% Scoring) │
│                                                             │
│ 5. Database Schema:     supabase/migrations/                │
│    (PostgreSQL DDL with RLS, Foreign Keys & Constraints)    │
│                                                             │
│ 6. Reproducible Seeds:  supabase/seed/seed.sql (Base)       │
│                         supabase/seed/02_all_india_districts│
│                         (Complete 784 LGD districts seed)   │
│    Verification SQL:    supabase/verify/                    │
│                         verify_location_master.sql          │
│                                                             │
│ 7. Automated Tests:     tests/                              │
│    (49 passing checks: 14 matching tests & 35 data integrity│
│     checks enforcing exact 784 districts and zero subsets)  │
└─────────────────────────────────────────────────────────────┘
```

* **Frontend**: Client-side React 19 Single Page Application with zero visual regressions.
* **National Location Master**: Authoritative Government of India master based on Local Government Directory (LGD), Ministry of Panchayati Raj (`data/raw/lgd_districts.xls.xlsx`), canonicalized into `src/data/canonicalLocations.json`, exposed via `src/data/locations.js`, and seeded via `supabase/seed/02_all_india_districts.sql`. Remote Supabase execution is a separate manual step if not performed directly.
* **Database Foundation**: Complete Supabase-compatible PostgreSQL schema and seed migrations created; Phase 2A live verification confirmed the configured project contains the expected 36 states/UTs, 784 districts, 7 opportunities, and mapped skills.
* **Deterministic Matching Engine**: Fully implemented and validated via test cases.
* **Temporary Fallback**: `src/data/mockOpportunities.js` is preserved as an in-memory fallback until Phase 3 connects the live database via the FastAPI backend.

---

### Implemented Backend Architecture (Phase 2 Implemented)

```
┌─────────────────────────────────────────────────────────────┐
│                    Utthan React Frontend                    │
│            (Preserved Cultural UI + Responsive SPA)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON API (/api/*)
                               │ (CORS Restricted: FRONTEND_ORIGIN)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Gateway                  │
│                     (backend/app/main.py)                   │
│                                                             │
│ • Health Routes:         /api/health, /api/health/db        │
│ • Location Routes:       /api/locations/states, districts   │
│ • Opportunities Routes:  /api/opportunities, /{id}          │
│ • Security Boundary:     Service Role Key isolated on server│
│ • OpenAPI Documentation: /docs, /redoc                      │
└──────────────────────────────┬──────────────────────────────┘
                               │ Server-side Client (supabase-py)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supabase PostgreSQL                      │
│ (36 States, 784 Districts, 11 Skills, 7 Opportunities, RLS) │
└─────────────────────────────────────────────────────────────┘
```

#### Security Boundary & Credential Isolation Rules
1. **Server-Side Exclusivity**: `SUPABASE_SERVICE_ROLE_KEY` and backend secrets are loaded exclusively by the Python FastAPI server (`backend/app/core/config.py`).
2. **Zero Frontend Secret Exposure**: Browser JavaScript and React frontend bundles NEVER receive the service-role key. No `VITE_` variable may ever be created for the service-role key.
3. **CORS Enforcement**: The FastAPI backend enforces strict CORS headers allowing requests exclusively from the designated `FRONTEND_ORIGIN` (default: `http://localhost:5173`).
4. **Resilient Failure Mode**: If Supabase credentials are missing or unconfigured, the backend reports clean diagnostic status codes (`503 Service Unavailable`) on `/api/health/db` without crashing or returning unvetted mock data.

---

### Target Architecture (Phase 3 & Future Planned)

```
┌─────────────────────────────────────────────────────────────┐
│                    Utthan React Frontend                    │
│            (Preserved Cultural UI + Responsive SPA)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Server                   │
│    (API Gateway, Rate Limiting, Secret Guard & Proxy Layer) │
└──────┬───────────────────────┼───────────────────────┬──────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌────────────────┐
│  PostgreSQL  │       │Recommendation│       │   AI & Voice   │
│  / Supabase  │       │    Engine    │       │ Proxy Service  │
│ (Persistent  │       │(Deterministic│       │ (Groq, Sarvam, │
│  Entities)   │       │ + Ranking)   │       │   BHASHINI)    │
└──────────────┘       └──────────────┘       └────────────────┘
```

In the target architecture:
1. **Frontend** communicates solely with the FastAPI backend.
2. **Third-party credentials** (`GROQ_API_KEY`, `SARVAM_API_KEY`, `BHASHINI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) exist exclusively on the server and are never exposed to the client.
3. **Persistent data** is managed through structured PostgreSQL tables in Supabase.

---

## 2. Planned Data Entities (Phase 1 Target)

These entities represent the planning data model to be implemented in Phase 1:

### 1. `beneficiaries`
Stores anonymous or identified citizen profile data gathered during onboarding.
* `id`: UUID (Primary Key)
* `name`: Text (optional/self-reported)
* `language`: Text (ISO code, e.g., 'hi', 'bn', 'ta')
* `state`: Text (Standardized State/UT name)
* `district`: Text (Standardized District name)
* `education`: Text ('8th_pass_or_below', '10th_pass', '12th_pass', 'iti_vocational', 'no_formal_schooling')
* `current_trade`: Text (Current occupation or prior experience)
* `mobility_preference`: Text ('village_block', 'within_15km', 'district_wide', 'relocate_with_hostel')
* `created_at`: Timestamp with time zone
* `updated_at`: Timestamp with time zone

### 2. `interview_sessions`
Records citizen voice/text conversational answers for auditability and recommendation tuning.
* `id`: UUID (Primary Key)
* `beneficiary_id`: UUID (Foreign Key $\rightarrow$ `beneficiaries.id`)
* `responses`: JSONB (Structured key-value pairs of responses)
* `transcript_log`: Text (Aggregated user transcript)
* `language`: Text
* `created_at`: Timestamp with time zone

### 3. `opportunities`
Master catalog of government welfare schemes, skill training programs, and grants.
* `id`: UUID / Text (e.g., 'opp-pm-vishwakarma-solar')
* `title`: Text (Scheme / opportunity title)
* `description`: Text (Comprehensive summary)
* `category`: Text ('Green Energy', 'Traditional Craft', 'Agri-Tech', 'Healthcare', 'Dairy', etc.)
* `partner_agency`: Text (e.g., 'PM Surya Ghar', 'NSDC', 'Ministry of Textiles')
* `state`: Text (Nullable; null indicates Pan-India scheme)
* `district`: Text (Nullable; null indicates all districts in state)
* `min_age`: Integer (Default 18)
* `max_age`: Integer (Nullable)
* `education_requirement`: Text (Minimum education level required)
* `mobility_requirement`: Text
* `stipend`: Text (Stipend description, e.g., '₹4,500 / month')
* `avg_earnings`: Text (Estimated post-placement earnings)
* `nsqf_level`: Integer (1 to 8, or null for non-NSQF schemes)
* `source_url`: Text (Official government portal link)
* `active`: Boolean (Default true)
* `created_at`: Timestamp with time zone
* `updated_at`: Timestamp with time zone

### 4. `skills`
Repository of standardized vocational skills and competencies.
* `id`: UUID / Text
* `name`: Text (e.g., 'Solar Rooftop Installation')
* `nsqf_level`: Integer (1 to 8)
* `sector`: Text (e.g., 'Green Jobs', 'Textiles & Apparel')
* `description`: Text

### 5. `opportunity_skills`
Many-to-many relationship mapping opportunities to required and taught skills.
* `opportunity_id`: Foreign Key $\rightarrow$ `opportunities.id`
* `skill_id`: Foreign Key $\rightarrow$ `skills.id`
* `is_taught`: Boolean (True if provided by training, false if pre-requisite)

### 6. `applications`
Local tracker for citizen pathway progress.
* `id`: UUID (Primary Key)
* `beneficiary_id`: UUID (Foreign Key $\rightarrow$ `beneficiaries.id`)
* `opportunity_id`: UUID (Foreign Key $\rightarrow$ `opportunities.id`)
* `status`: Text ('saved', 'enrolled', 'in_progress', 'completed')
* `current_step`: Integer (Current milestone index)
* `created_at`: Timestamp with time zone

---

## 3. Planned Recommendation Architecture

### Core Design Principle: Deterministic Eligibility First
> **Critical Rule:** The LLM does NOT decide whether a citizen is legally eligible for a government program. Eligibility is strictly deterministic based on statutory criteria (State/District, Education, Age, Category).

```
Citizen Input (Location, Education, Mobility, Trade Interest)
                            ↓
       ┌────────────────────────────────────────┐
       │   1. Deterministic Eligibility Filter  │
       │   - State / District match             │
       │   - Education threshold match          │
       │   - Target demographic filter          │
       └───────────────────┬────────────────────┘
                           │ Eligible Schemes Pool
                           ▼
       ┌────────────────────────────────────────┐
       │   2. Rule-Based Scoring & Ranking      │
       │   - Trade alignment weight (40%)       │
       │   - Mobility tolerance weight (25%)    │
       │   - Educational fit weight (20%)       │
       │   - Goal priority weight (15%)         │
       └───────────────────┬────────────────────┘
                           │ Ranked Top-N Matches
                           ▼
       ┌────────────────────────────────────────┐
       │   3. Contextual Reasoning (Groq AI)   │
       │   - Explains in citizen's mother tongue│
       │   - "Why this matches your situation"  │
       │   - Summarizes practical next steps    │
       └───────────────────┬────────────────────┘
                           ▼
                 Delivered to Frontend
```

---

## 4. Voice & Multilingual Architecture

### Speech-to-Text (STT)
* **Current**: Native Browser Web Speech API (`window.webkitSpeechRecognition`).
* **Limitation**: Requires Chromium browsers (Chrome/Edge desktop, Chrome Android).
* **Future**: Server-side Bhashini Speech-to-Text once official approvals and API keys are provisioned.

### Text-to-Speech (TTS)
* **Current**: Sarvam AI API (`Bulbul:v3`) with single-session concurrency guard and browser `speechSynthesis` fallback.
* **Currently Configured Languages in Sarvam Map (11)**:
  `hi`, `bn`, `ta`, `te`, `mr`, `gu`, `kn`, `ml`, `pa`, `or`, `en`.
* **Fallback for Other 12 Scheduled Languages**:
  Browser `speechSynthesis` with native voice matching.
* **Future**: Bhashini Indic TTS for complete 22-language official coverage.
