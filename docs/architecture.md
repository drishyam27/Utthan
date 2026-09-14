# Utthan (उत्थान) — Architecture & Technical Specifications

> **Notice:** This document defines the architectural baseline for Phase 0 and the target specifications for future implementation phases. It explicitly differentiates between currently implemented components and planned/future components.

---

## 1. System Architecture Overview

### Current Implementation Baseline (Phase 0)

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
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
    ┌─────────────────────┐        ┌─────────────────────┐
    │      Groq API       │        │    Sarvam AI API    │
    │ (qwen/qwen3.6-27b)  │        │ (Bulbul:v3 IndicTTS)│
    │ [ORPHANED IN CODE]  │        │  [ACTIVE FOR TTS]   │
    └─────────────────────┘        └─────────────────────┘
               │
               ▼
    ┌─────────────────────────────────────────────────────────┐
    │            src/data/mockOpportunities.js                │
    │     [100% HARDCODED / MOCK DATA - 5 STATIC SCHEMES]     │
    └─────────────────────────────────────────────────────────┘
```

* **Frontend**: Client-side React 19 Single Page Application. Page navigation managed via component state in `src/App.jsx`.
* **Backend**: None. No API server or proxy exists.
* **Database**: None. Data resets on browser reload.
* **Security Context**: Uses client-side `VITE_GROQ_API_KEY` and `VITE_SARVAM_API_KEY`. These keys are exposed in client network requests and are suitable for local evaluation only.

---

### Target Architecture (Planned / Future)

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
