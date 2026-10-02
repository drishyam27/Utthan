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
* **Temporary Fallback**: `src/data/mockOpportunities.js` remains preserved for the existing admin/demo surface; the citizen opportunity list and detail flow now use FastAPI.

---

### Implemented Backend Architecture (Phase 2B Implemented)

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
│ • Location Routes:       /api/locations/states, districts,  │
│                          /api/locations/resolve             │
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

#### Automatic Location Resolution (Phase 2B)

1. The React onboarding flow collects a transient display name, then requests browser geolocation only when the user reaches the location step and explicitly taps the location-access button.
2. Latitude, longitude, and optional accuracy are sent transiently to `POST /api/locations/resolve`; raw coordinates are not persisted, placed in browser storage, echoed in responses, or logged by the application.
3. FastAPI delegates reverse geocoding through a provider adapter. The development default is a configurable Nominatim adapter using `httpx`; production requires an approved provider and any associated credentials/configuration.
4. The resolver rejects unsupported, unavailable, ambiguous, outside-India, or non-canonical results. State and District names must match exactly one record in the Supabase LGD master before canonical IDs are returned.
5. The frontend uses only the canonical State/District response for the opportunity filter and user-facing location display.

#### Phase 2C-1 Data and Security Foundation

Phase 2C-1 prepares contracts and database structure without exposing new API routes or changing the frontend flow:

1. Stable beneficiary fields remain the existing name, language, canonical State/District IDs, education, occupation, mobility, and primary goal values.
2. `interview_sessions` retains structured JSON answers and gains draft/completed status, revision, timestamps, and nullable extracted-profile JSON for later deterministic extraction.
3. `beneficiary_sessions` stores only a server-side hash of a high-entropy anonymous capability token, with expiry, rotation, last-use, and revocation metadata. Raw tokens are never stored or logged.
4. Beneficiary, interview, capability-session, and application tables are private to the FastAPI service-role boundary. Existing public catalog reads for states, districts, skills, opportunities, and opportunity-skills remain available.
5. Recommendation responses have a typed contract for eligibility, score, matched/unmet criteria, reasons, NSQF level, QP code, and verified skill metadata. Live recommendation APIs remain deferred.
6. The deterministic matcher rejects restricted opportunities when canonical beneficiary location is missing; no location is inferred.

Phase 2C-1 intentionally does not implement beneficiary APIs, interview APIs, recommendation APIs, frontend persistence, authentication, or AI/voice providers.

#### Phase 2C-2 Anonymous Beneficiary Profile API

Phase 2C-2 connects the existing onboarding/profile flow to the Phase 2C-1 persistence boundary:

1. `POST /api/beneficiaries` validates the onboarding name, language, and canonical State/District IDs, creates the beneficiary, and returns the opaque capability token once.
2. `GET /api/beneficiaries/{id}` and `PATCH /api/beneficiaries/{id}` require `Authorization: Bearer <capability-token>`. The token is hashed for lookup, checked for expiry/revocation, and must belong to the requested beneficiary.
3. The backend uses the service-role Supabase client. Public beneficiary access is not restored and the service-role key never reaches the browser.
4. The frontend stores only the anonymous session capability and beneficiary ID in browser `sessionStorage`, hydrates the profile after refresh, and clears the capability on an unauthorized response. It uses the existing `VITE_API_BASE_URL` configuration; no new frontend secret is required.
5. Profile updates use an allowlist of beneficiary fields. Canonical State/District relationships are validated server-side; raw coordinates and interview answers are not persisted in this phase.

The Phase 2C-1 migration must be applied manually before these endpoints can persist against a live Supabase project. Phase 2C-3 interview persistence, recommendation APIs, authentication, and AI/voice integration remain deferred.

#### Phase 2C-3 Persistent Interview Lifecycle

Phase 2C-3 makes the existing four-question interview refresh-safe while preserving its established UI, keys, option values, and browser speech behavior:

1. `POST /api/beneficiaries/{beneficiary_id}/interviews` authenticates the beneficiary capability and creates one draft session, or resumes the latest existing session. A completed session is returned as completed and is never silently reopened.
2. `GET /api/interviews/{interview_id}` returns only the interview owned by the capability-resolved beneficiary. `PATCH /api/interviews/{interview_id}` replaces the validated structured responses for a draft and requires the caller's expected revision.
3. `POST /api/interviews/{interview_id}/complete` validates all four established response dimensions (`workInterest`, `education`, `mobility`, and the existing UI key `preference` for primary goal), transitions the row to `completed`, sets `completed_at`, and increments the revision.
4. Draft writes and completion use an optimistic revision check. Stale writes return `409 Conflict`; completed sessions reject edits and cannot revert to draft. The frontend treats React state as a cache and FastAPI/Supabase as the source of truth.
5. The existing onboarding persists the beneficiary before entering the interview, then the frontend creates/resumes the interview, saves each answer, restores answers after refresh, and completes through FastAPI. Capability expiry/revocation returns the user to the existing onboarding recovery path.
6. No new migration was required: the applied Phase 2C-1 migration already provides the required interview lifecycle columns and private service-role persistence boundary. `extracted_profile` remains `NULL`; no recommendations, AI/LLM extraction, or voice-provider changes are implemented.

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

## 3. Deterministic Recommendation Architecture

### Core Design Principle: Deterministic Eligibility First
> **Critical Rule:** The LLM does NOT decide whether a citizen is legally eligible for a government program. Eligibility is strictly deterministic based on statutory criteria (State/District, Education, Age, Mobility).

```
Beneficiary Profile + Completed Interview Responses
                            ↓
       ┌────────────────────────────────────────┐
       │   1. Deterministic Eligibility Filter  │
       │   - Geography (Pan-India vs LGD State) │
       │   - Canonical location required        │
       │   - Minimum Education threshold rank   │
       │   - Age boundaries (if provided)       │
       │   - Mobility requirement rank          │
       └───────────────────┬────────────────────┘
                           │ Eligible Schemes Pool
                           ▼
       ┌────────────────────────────────────────┐
       │   2. Rule-Based Scoring & Ranking      │
       │   - Trade / craft alignment (40%)      │
       │   - Mobility preference fit (25%)      │
       │   - Educational pace fit (20%)         │
       │   - Goal / milestone priority fit (15%)│
       │   - Deterministic Tie-Breaker:         │
       │     score DESC, nsqf DESC, opp_id ASC  │
       └───────────────────┬────────────────────┘
                           │ Ranked Top-N Matches + Explainable Ineligible Pool
                           ▼
       ┌────────────────────────────────────────┐
       │   3. Capability-Protected API Response │
       │   - GET /api/beneficiaries/{id}/recs   │
       │   - NSQF QP code & skills metadata     │
       │   - Explicit matched & unmet criteria  │
       └────────────────────────────────────────┘
```

### Phase 2C-4 Implementation Details
* **Protected Endpoint**: `GET /api/beneficiaries/{beneficiary_id}/recommendations`
* **Authentication**: Capability Bearer Token (validated against `beneficiary_sessions.token_hash` with expiry and revocation check).
* **Missing Interview Handling**: If no interview has been completed, returns HTTP 200 with `has_completed_interview: false`, `recommendations: []`, and an informative message without fabricating recommendations.
* **Canonical Location Strictness**: Missing or unresolved State/District rejects restricted opportunities without guessing or inferring location.
* **Scoring Weights (100% total)**:
  - Trade Alignment: 40 points max (keyword match = 40, category cluster = 25, fallback = 15).
  - Mobility Fit: 25 points max (exact commute match = 25, regional commute = 18).
  - Education Fit: 20 points max (exact qualification pace = 20, exceeding base = 17).
  - Goal Fit: 15 points max (direct milestone match = 15, complementary = 10).
* **Tie-Breaker**: Secondary sort on `nsqf_level` DESC, tertiary sort on `opportunity_id` ASC.
* **Separation of Concerns**: Returns `recommendations` (strictly eligible) and `ineligible_opportunities` (with `eligible: false` and explicit `unmet_criteria`).

### Phase 2C-5 Implementation Details (Frontend Integration)
* **API Client Consumption**: `src/services/api.js` defines `fetchRecommendations(beneficiaryId, sessionToken)` calling `GET /api/beneficiaries/{beneficiary_id}/recommendations` with the standard `Authorization: Bearer <token>` capability header.
* **Architecture Preservation**: Backend remains the sole authoritative source of truth. Zero client-side re-scoring, re-ranking, or eligibility filtering is implemented in React.
* **Opportunity Adapter Extension**: `src/services/opportunityAdapter.js` normalizes recommendation payload fields (`score` $\rightarrow$ `matchScore`, `matched_criteria` $\rightarrow$ `matchedCriteria`, `unmet_criteria` $\rightarrow$ `unmetCriteria`, `why_matches` $\rightarrow$ `reasons`).
* **UX States Handled in `OpportunitiesPage`**:
  1. *Loading*: Accessible skeleton shimmer feedback.
  2. *Recommendations Available*: Badges highlighting profile match score (e.g., `85% Profile Match`), reasons why recommended (`Why this is recommended`), and matched criteria pills.
  3. *Incomplete Interview*: Action card explaining that livelihood assessment is required, linking directly to `ConversationPage`.
  4. *No Eligible Matches*: Contextual empty state with transparent disclosure of ineligible schemes and unmet statutory criteria.
  5. *API Error / Network Failure*: Graceful error boundary state with safe retry button without exposing backend stack traces.

---

## 4. Voice & Multilingual Architecture

### Speech-to-Text (STT) (Phase 2C-6 Implemented)
* **Primary Provider**: Sarvam AI `saaras:v4` Multilingual Speech-to-Text API (`POST https://api.sarvam.ai/speech-to-text`).
* **Backend Endpoint**: `POST /api/voice/transcribe` (multipart/form-data with in-memory streaming).
* **Security & Credential Isolation**:
  - `SARVAM_API_KEY` is loaded exclusively by the backend (`Settings.SARVAM_API_KEY`).
  - Browser JavaScript bundles never receive or store the Sarvam API key.
  - Rate limiting (429), timeouts (504), and upstream errors (502) are sanitized so no keys or internal URLs leak to the client.
* **Privacy & In-Memory Processing**:
  - Voice recordings are streamed in-memory via `UploadFile.read()`.
  - Zero disk caching or persistent storage of citizen voice recordings.
  - Memory buffers are released immediately upon completion of the transcription request.
* **Audio Capture & Codecs**:
  - Browser client uses `MediaRecorder` API via `src/services/audioRecorder.js`.
  - Supports `audio/webm`, `audio/wav`, `audio/ogg`, and `audio/mp4` containers up to 10 MB.
  - Client state machine manages explicit states: `idle`, `recording`, `transcribing`, and `error`.
* **Language Support (22 Official Languages + Indian English)**:
  - Maps Utthan language IDs to official BCP-47 codes: `hi-IN`, `bn-IN`, `ta-IN`, `te-IN`, `mr-IN`, `gu-IN`, `kn-IN`, `ml-IN`, `pa-IN`, `od-IN`, `as-IN`, `mai-IN`, `sa-IN`, `ne-IN`, `kok-IN`, `sd-IN`, `ks-IN`, `doi-IN`, `mni-IN`, `brx-IN`, `sat-IN`, `en-IN`.
  - Falls back to `unknown` for automatic language detection by the provider.
* **Fallback Strategy**:
  - If `MediaRecorder` is unsupported on older browsers or mobile web views, gracefully falls back to the native Chromium Web Speech API (`SpeechRecognition`).
* **Downstream Integration**:
  - Transcripts flow directly into conversational input and option matcher (`matchTranscriptToOption`), maintaining strict parity with persisted interview schemas. Groq LLM integration will consume these transcripts in Phase 3.

### Text-to-Speech (TTS)
* **Current**: Sarvam AI API (`Bulbul:v3`) with single-session concurrency guard and browser `speechSynthesis` fallback.
* **Currently Configured Languages in Sarvam Map (11)**:
  `hi`, `bn`, `ta`, `te`, `mr`, `gu`, `kn`, `ml`, `pa`, `or`, `en`.
* **Fallback for Other 12 Scheduled Languages**:
  Browser `speechSynthesis` with native voice matching.
* **Future**: Bhashini Indic TTS for complete 22-language official coverage.
