# 📌 Utthan (उत्थान) — Project Progress & Feature Tracker

> **Utthan** is an AI-powered, multilingual public service and livelihood pathway platform designed for Indian citizens. It bridges grassroots job seekers, rural artisans, and youth with government-certified training schemes, stipends, and dignified economic opportunities through voice-first, culturally authentic interfaces.

---

## 📊 Summary Status

- **Status**: Phase 2C-2 Complete — Anonymous Beneficiary/Profile API Complete
- **Current Development Phase**: Phase 2C-2 (Beneficiary/Profile API)
- **Next Development Phase**: Phase 2C-3 (Interview Persistence)
- **Supported Languages**: 23 (English + All 22 Official Eighth Schedule Indian Languages)
- **Primary Tech Stack**: React 19, Vite 8, Tailwind CSS 3.4, FastAPI, Pydantic, Supabase / PostgreSQL
- **Target Form Factors**: Responsive Web (Optimized for Mobile Portrait & Desktop Landscape)

---

## 🚦 Component Status Overview

| Component | Status | Current Reality | Next Phase Action |
|---|---|---|---|
| **Visual UI & Design System** | **COMPLETED** | Polished, responsive cultural theme, light-calibrated mode | Preserve without visual redesign |
| **Multilingual UI (23 Langs)** | **COMPLETED** | UI translations dictionary and native scripts active | Maintain and keep synced |
| **Voice Playback (TTS)** | **PARTIALLY COMPLETED** | Sarvam AI Bulbul:v3 active for 11 languages; browser fallback for 12 | Expand coverage in voice service |
| **Voice Input (STT)** | **PARTIALLY COMPLETED** | Native browser Web Speech API (Chromium-supported) | Evaluate Bhashini / Sarvam STT |
| **State & District Dataset** | **COMPLETED** | Authoritative 36 States/UTs & 784 districts from LGD master in `canonicalLocations.json` & `locations.js`; automatic resolution validates against the same Supabase master | Use canonical IDs in later profile/recommendation work |
| **Verified Opportunities Data**| **COMPLETED** | 7 verified government schemes with NSQF & portal source links | Served via `/api/opportunities` |
| **Skills Catalog (NSQF)** | **COMPLETED** | 11 standardized skills with official SSC QP codes & levels | Embedded in opportunity details |
| **Recommendation Engine** | **COMPLETED** | Deterministic eligibility checks & weighted scoring in `recommendationEngine.js` | Connect to backend in Phase 3 |
| **Database Schema & Seed** | **COMPLETED** | Full PostgreSQL DDL in `supabase/migrations/` & 784-district seed in `supabase/seed/02_all_india_districts.sql` | Verified in Supabase |
| **Groq AI Integration** | **PARTIALLY COMPLETED** | Inference function declared in `aiService.js` (uncalled in UI) | Connect to profile extraction in Phase 3 |
| **Backend API (FastAPI)** | **COMPLETED** | FastAPI modular backend with health, location, automatic location-resolution, opportunity, and anonymous beneficiary profile routes | Add interview/recommendation APIs in later phases |
| **BHASHINI Integration** | **BLOCKED** | Approval & API credentials pending | Retain Sarvam AI fallback until unblocked |

---

## 🚀 Strict Phase-by-Phase Roadmap

### ✅ Phase 0: Repository, Environment & Architecture Preparation (COMPLETED)
- [x] Full technical audit and implementation baseline documentation.
- [x] Environment variable isolation verification (`.gitignore` protection).
- [x] Formal system architecture and planned entity model documentation (`docs/architecture.md`).
- [x] Deterministic recommendation pipeline design.
- [x] Verification of existing UI functionality, clean build (`npm run build`), and zero breaking changes.

### ✅ Phase 1: Data Foundations & Real Opportunity Engine (COMPLETED)
- [x] Complete authoritative national master of 36 Indian States/UTs and 784 districts from Local Government Directory (`src/data/canonicalLocations.json` & `src/data/locations.js`).
- [x] Complete 784-district database seed script (`supabase/seed/02_all_india_districts.sql`) with verification script (`supabase/verify/verify_location_master.sql`).
- [x] PostgreSQL / Supabase schema for `states`, `districts`, `skills`, `opportunities`, `opportunity_skills`, `beneficiaries`, `interview_sessions`, and `applications` (`supabase/migrations/20260915000001_initial_schema.sql`).
- [x] Verified opportunity dataset (PM Vishwakarma, PM Surya Ghar, PMKVY 4.0, DDU-GKY, Lakhpati Didi, PM-AJAY GIA) with official sources, eligibility criteria, and NSQF levels.
- [x] Standardized skills catalog with Sector Skill Council QP codes.
- [x] Deterministic eligibility rules engine & weighted scoring matrix (`src/services/recommendationEngine.js`).
- [x] Automated test suite passing 49 checks for matching cases & national data integrity (`npm test`).
- [x] Preserved `mockOpportunities.js` as temporary frontend fallback without breaking the UI.

### ✅ Phase 2: FastAPI Backend / API Foundation (COMPLETED)
- [x] Modular FastAPI backend application entry point (`backend/app/main.py`).
- [x] Environment and secret configuration with strict frontend isolation (`backend/app/core/config.py`, `backend/.env.example`).
- [x] Supabase server-side connection client with graceful disconnected handling (`backend/app/db/supabase.py`).
- [x] Health check endpoints: `GET /api/health` and `GET /api/health/db` (`backend/app/api/routes/health.py`).
- [x] Location endpoints serving authoritative LGD data: `GET /api/locations/states` and `GET /api/locations/states/{state_code}/districts` (`backend/app/api/routes/locations.py`).
- [x] Opportunity endpoints with filtering and skills expansion: `GET /api/opportunities` and `GET /api/opportunities/{opportunity_id}` (`backend/app/api/routes/opportunities.py`).
- [x] Clean Pydantic response schemas (`backend/app/schemas/`).
- [x] Configurable CORS middleware supporting `FRONTEND_ORIGIN` (`http://localhost:5173`).
- [x] Automatic OpenAPI documentation (`/docs`, `/redoc`).
- [x] Automated backend test suite with 15 passing tests (`pytest backend/tests`).
- [x] Zero frontend redesign or breakage; frontend build (`npm run build`) and tests (`npm test`) fully intact.

### ✅ Phase 2A: Supabase + Backend Live Verification & Stabilization (COMPLETED)
- [x] Made `lgd_code` and `lgd_district_code` part of the reproducible initial schema while retaining backward-compatible seed guards.
- [x] Preserved the additive PostgREST permissions/schema-cache repair migration for existing Supabase projects.
- [x] Live-verified the configured Supabase project: 36 States/UTs, 784 districts, 7 opportunities, mapped skills, expected API routes, and negative cases.
- [x] Sanitized production-facing backend error responses and added server-side exception logging.
- [x] Standardized backend test fixtures on the production `priority` mapping field.
- [x] Confirmed frontend/backend integration remains intentionally pending for a later phase.

### ✅ Phase 2B: Automatic Location Detection & React/FastAPI Integration (COMPLETED)
- [x] Added the minimal Language → Name → Location onboarding sequence; geolocation is user-triggered and normal onboarding does not ask beneficiaries to manually select State/District.
- [x] Added `POST /api/locations/resolve` with strict coordinate validation, provider abstraction, generic failure handling, and exact LGD/Supabase State/District validation.
- [x] Kept raw latitude/longitude transient: no persistence, browser storage, response echo, or coordinate logging.
- [x] Added the `VITE_API_BASE_URL` frontend API client and connected live opportunities list/detail screens to FastAPI without production mock fallback.
- [x] Preserved the existing visual design and retained `mockOpportunities.js` only for the existing admin/demo surface that still imports it.
- [x] Added mocked-provider backend coverage for valid, malformed, unresolved, ambiguous, outside-India, and provider-failure cases.
- [x] Verified backend tests, frontend tests, lint, production build, and live API contract checks.

### ✅ Phase 2C-1: Data Contract & Schema Foundation (COMPLETED)
- [x] Added typed backend contracts for beneficiary profiles, interview lifecycle, anonymous sessions, and deterministic recommendation responses.
- [x] Added an additive migration for interview status, revision, completion timestamp, extracted profile JSON, and anonymous capability sessions.
- [x] Restricted direct anonymous/authenticated access to beneficiary, interview, session, and application persistence tables; catalog read policies remain unchanged.
- [x] Added high-entropy anonymous capability token generation and server-side SHA-256 hash verification helpers without API or login implementation.
- [x] Enforced the existing application categorical values in backend contracts and database constraints.
- [x] Corrected deterministic recommendation behavior so restricted opportunities require canonical beneficiary State/District identifiers.
- [x] Added focused Phase 2C-1 contract, security-helper, migration-assumption, and missing-location tests.
- [x] Intentionally deferred beneficiary APIs, interview APIs, recommendation APIs, frontend persistence, and all AI/voice/authentication work.

### ✅ Phase 2C-2: Beneficiary/Profile API (COMPLETED)
- [x] Added anonymous beneficiary create, retrieve, and partial-update endpoints with generic safe errors.
- [x] Validated canonical State/District identifiers and rejected arbitrary or mismatched location pairs.
- [x] Reused the Phase 2C-1 capability-token hash model with expiry, revocation, last-use tracking, and beneficiary ownership checks.
- [x] Connected onboarding completion to beneficiary persistence and retained the capability in session-scoped browser storage.
- [x] Restored the persisted beneficiary profile after refresh and connected existing profile editing to PATCH updates without redesigning the UI.
- [x] Added backend API/security tests and frontend capability-storage coverage.
- [x] Kept interview persistence, recommendation APIs, authentication, and AI/voice integration deferred.

### ⏳ Phase 2C-3: Interview Persistence (NOT STARTED)
- [ ] Implement draft, resume, answer-save, completion, revision, and idempotency APIs.

### ⏳ Phase 2C-4: Deterministic Recommendation Service (NOT STARTED)
- [ ] Move the verified matching logic behind a single backend recommendation service.

### ⏳ Phase 2C: Profile, Recommendation & AI Backend Integration (NOT STARTED)
- [ ] Connect the resolved canonical location and interview profile to deterministic backend recommendations.
- [ ] Add server-side profile persistence and authentication boundaries.
- [ ] Move approved AI/voice provider integrations behind the backend gateway.

### ⏳ Phase 3: Adaptive Voice Interview & Profile Extraction (NOT STARTED)
- [ ] Onboarding flow capturing Beneficiary Name, State, and District.
- [ ] Conversational interview connected to Groq LLM for semantic profile extraction.
- [ ] Voice prompt synchronizer with Sarvam TTS.
- [ ] Dynamic opportunity matching triggered upon interview completion.

### ⏳ Phase 4: Citizen Engagement, Persistence & PWA (NOT STARTED)
- [ ] Local storage and database persistence for citizen skill profiles.
- [ ] Downloadable application receipt (PDF / Image) with QR code.
- [ ] PWA offline asset caching for low-connectivity rural environments.

---

### 2. 🌐 Multilingual Engine (23 Languages)
Full localization configuration with native scripts, greetings, hero headers, voice prompts, and placeholder text in `src/data/languages.js`:

- [x] **English** (`en`) — English
- [x] **Hindi** (`hi`) — हिन्दी
- [x] **Bengali** (`bn`) — বাংলা
- [x] **Telugu** (`te`) — తెలుగు
- [x] **Marathi** (`mr`) — मराठी
- [x] **Tamil** (`ta`) — தமிழ்
- [x] **Urdu** (`ur`) — اردو
- [x] **Gujarati** (`gu`) — ગુજરાતી
- [x] **Kannada** (`kn`) — ಕನ್ನಡ
- [x] **Malayalam** (`ml`) — മലയാളം
- [x] **Odia** (`or`) — ଓଡ଼ିଆ
- [x] **Punjabi** (`pa`) — ਪੰਜਾਬੀ
- [x] **Assamese** (`as`) — অসমীয়া
- [x] **Maithili** (`mai`) — मैथिली
- [x] **Sanskrit** (`sa`) — संस्कृतम्
- [x] **Nepali** (`ne`) — नेपाली
- [x] **Konkani** (`kok`) — कोंकणी
- [x] **Sindhi** (`sd`) — سنڌي / सिंधी
- [x] **Kashmiri** (`ks`) — کٲشُر / कॉशुर
- [x] **Dogri** (`dgo`) — डोगरी
- [x] **Manipuri / Meitei** (`mni`) — মৈতৈলোন্
- [x] **Bodo** (`brx`) — बड़ो
- [x] **Santali** (`sat`) — ᱥᱟᱱᱛᱟᱲᱤ
- [x] **Instant Language Search**: Fast search bar in the language modal filtering by English name or native script.
- [x] **Script Family Badges**: Badges indicating Devanagari, Gurmukhi, Ol Chiki, Perso-Arabic, Dravidian, etc.

---

### 3. 📱 Pages & Core Flows

| Page Component | Path | Status | Key Features |
|---|---|---|---|
| **Landing Page** | `src/pages/LandingPage.jsx` | ✅ Complete | Hero headline, animated microphone button (`VoiceButton.jsx`), "or type instead" toggle, popular pathway discovery pills. |
| **Language Selection** | `src/pages/LanguagePage.jsx` | ✅ Complete | Modal & full page modes, 23 language cards, live search, script tags, active check indicator. |
| **Conversational Onboarding** | `src/pages/ConversationPage.jsx` | ✅ Complete | Step-by-step interactive questionnaire (interests, education, location), voice listening simulation, chat history. |
| **Opportunities Catalog** | `src/pages/OpportunitiesPage.jsx` | ✅ Complete | Categorized schemes (PMKVY, Skill India, PM Vishwakarma), stipend badges, district filter, search. |
| **Opportunity Details** | `src/pages/OpportunityDetailsPage.jsx` | ✅ Complete | Eligibility criteria, duration, training center contact info, document checklist, apply action. |
| **Action Pathway** | `src/pages/ActionPathPage.jsx` | ✅ Complete | Visual timeline roadmap (Step 1 to Placement), status progression, contact coordinator CTA. |
| **Citizen Profile** | `src/pages/ProfilePage.jsx` | ✅ Complete | Digital Skill Card, verified badges, active pathway tracker, application records. |
| **How to Use Guide** | `src/pages/HowToUsePage.jsx` | ✅ Complete | 5 visual step-by-step cards illustrated for rural and first-time digital users. |
| **Admin Dashboard** | `src/pages/AdminDashboard.jsx` | ✅ Complete | Government telemetry, language distribution charts, scheme conversion metrics, district analytics. |
| **Navbar & Mobile Drawer** | `src/components/Navbar.jsx` | ✅ Complete | Responsive navigation, mobile hamburger drawer, active language pill, portal switch. |

---

### 4. ⚙️ Server & Network Infrastructure
- [x] **Vite Dev Server Configuration**: Bound to all interfaces (`--host` / `0.0.0.0`) in `vite.config.js`.
- [x] **Host Header & CORS Whitelisting**: `allowedHosts: true` and `cors: true` configured.
- [x] **Mobile Hotspot Direct LAN Support**: Works via local IP (`http://<LAN-IP>:5173`) over private network profile.
- [x] **Remote Tunneling Verified**: Verified working over public HTTPS dev tunnels for remote previews.
- [x] **Clean Production Build**: Zero compilation errors (`npm run build` generates optimized `dist/`).

---

### 5. 🤖 Real AI & Multilingual Voice Integration (LIVE)
- [x] **Voice-First Step-by-Step Guided Assistant**:
  - Replaced chatbot bubble interface with a focused, voice-first step-by-step interview experience.
  - **Step 0 (Language Preference)**: AI takes input of preferred language at the very beginning. Supports both **Voice Input** (tap mic and speak "বাংলা", "Hindi", "Tamil", "Telugu", etc.) and **Option Cards** (all 22 Official Indian Languages + English).
  - **Live Full Website Translation**: Once a language is chosen, the entire website (Navbar links, subtitle in native script, hero headings, opportunity lists, action roadmaps, and footer) dynamically translates.
  - **Verbal Confirmation**: Sarvam AI speaks audio confirmation in the chosen language (e.g. in Bengali: *"বাংলা ভাষা নির্বাচন করা হয়েছে..."* or Hindi: *"हिन्दी भाषा चुनी गई है..."*).
  - **Step-by-Step Question Progression**: Steps 1 to 4 guide the citizen through Trade & Skills, Education, Travel, and Primary Goal, followed by AI-matched certified local opportunities.
- [x] **Groq LLM Engine**: Connected `qwen/qwen3.8-27b` via Groq API with multi-layer sanitization removing any internal thinking tags.
- [x] **Sarvam AI Indic Voice (Bulbul:v3)**: Integrated Sarvam AI Text-to-Speech (`speaker: priya`) producing natural Indian voice audio playback across Indic languages.
- [x] **Single-Voice Concurrency Lock & Echo Prevention**:
  - Implemented `AbortController` and a unique speech session ID in `aiService.js` to abort in-flight network requests.
  - Guarded step transitions with `lastSpokenStepRef` and `hasSpokenGreetingRef` so that only one voice plays at any time, eliminating echoes and overlapping voices.
- [x] **Real Web Speech Recognition**: Connected device microphone speech-to-text with multi-language keyword detection (`detectLanguageFromVoice`).
- [x] **Audio Controls**: Voice mute/unmute toggle, pause-on-tap, and replay audio question buttons.

---

## 🚀 Upcoming Roadmap / Backlog (What Still Needs to Be Made)

### Phase 2: State Persistence & Offline Capability
- [ ] **Local Storage Persistence**:
  - Save selected language, citizen profile data, and saved opportunities across page reloads.
- [ ] **PWA (Progressive Web App)**:
  - Add `manifest.json` and service worker so mobile users can tap **"Install Utthan"** / **"Add to Home Screen"**.
  - Cache core assets for low-connectivity rural environments.

### Phase 3: Citizen Engagement & Verification
- [ ] **Downloadable Application Receipt (PDF / Image)**:
  - Generate printable/sharable **Utthan Avedan Patra** with application number and QR code for Village CSC centers.
- [ ] **SMS / WhatsApp Alert Simulator**:
  - Simulate application confirmation SMS alerts for citizen reassurance.

### Phase 4: Government Portal & Scheme Backend
- [ ] **Live Open Government Scheme API**:
  - Connect with real public job feeds or ministry APIs (PMKVY / Skill India).

---

## 📂 Project Architecture

```
d:\Utthan\
├── public\
│   └── assets\
│       ├── utthan-bg.jpg            # Desktop authentic cultural landscape artwork
│       └── utthan-bg-mobile.jpg     # Mobile authentic cultural portrait artwork
├── src\
│   ├── components\
│   │   ├── CulturalBackground.jsx   # Responsive dual-mode light-calibrated background
│   │   ├── Navbar.jsx               # Header & mobile sliding navigation drawer
│   │   └── VoiceButton.jsx          # Circular animated pulse microphone button
│   ├── data\
│   │   ├── languages.js             # 23 official languages configuration & translations
│   │   └── mockOpportunities.js     # Certified training programs, stipends & schemes
│   ├── pages\
│   │   ├── ActionPathPage.jsx       # Roadmap timeline
│   │   ├── AdminDashboard.jsx       # Public administration & analytics portal
│   │   ├── ConversationPage.jsx     # Conversational questionnaire
│   │   ├── HowToUsePage.jsx         # 5-step visual guide
│   │   ├── LandingPage.jsx          # Editorial hero & voice entry
│   │   ├── LanguagePage.jsx         # 23-language selector & search
│   │   ├── OpportunitiesPage.jsx    # Scheme search & filter catalog
│   │   ├── OpportunityDetailsPage.jsx# Details, eligibility & center info
│   │   └── ProfilePage.jsx          # Digital skill passport
│   ├── App.jsx                      # App root router & state management
│   ├── index.css                    # Tailwind directives & design tokens
│   └── main.jsx                     # Vite React entrypoint
├── index.html                       # HTML5 template with SEO & Google Fonts
├── tailwind.config.js               # Theme colors, typography & animations
├── vite.config.js                   # Vite config with network host & CORS
├── tracker.md                       # Project progress & feature tracking
└── package.json                     # Dependencies & scripts
```

---

## 💻 Quick Commands

```bash
# Start local development server (accessible via localhost & LAN)
npm run dev -- --host

# Build production bundle
npm run build

# Preview production build locally
npm run preview
```

---
*Last Updated: September 2026*
