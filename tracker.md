# 📌 Utthan (उत्थान) — Project Progress & Feature Tracker

> **Utthan** is an AI-powered, multilingual public service and livelihood pathway platform designed for Indian citizens. It bridges grassroots job seekers, rural artisans, and youth with government-certified training schemes, stipends, and dignified economic opportunities through voice-first, culturally authentic interfaces.

---

## 📊 Summary Status

- **Status**: Active Development & MVP Feature-Complete
- **Supported Languages**: 23 (English + All 22 Official Eighth Schedule Indian Languages)
- **Primary Tech Stack**: React 18, Vite 6, Tailwind CSS, Lucide Icons, Web Speech API Architecture
- **Target Form Factors**: Responsive Web (Optimized for Mobile Portrait & Desktop Landscape)

---

## ✅ Completed Features & Milestones

### 1. 🎨 Visual Design & Cultural Assets
- [x] **Desktop Authentic Background**: High-resolution landscape artwork (`utthan-bg.jpg`) active on viewports $\ge$ 768px.
- [x] **Mobile Authentic Background**: High-resolution portrait artwork (`utthan-bg-mobile.jpg`) active on viewports < 768px.
- [x] **Calibrated Light Mode**:
  - Softened background saturation (`saturate-[0.70]`) and tuned brightness (`brightness-[1.20]`).
  - Warm cream/off-white background base (`#FAF7F0`) with 50% artwork opacity.
  - Ambient central radial glow for maximum readability of text, cards, and CTA buttons.
- [x] **Cultural Motif Preservation**: Authentic Indian rural symbols preserved (Alpana/Mandala, crops/paddy, sewing machine, bobbin/thread, wicker basket, cow and calf, fish/fisheries, wheel edger/plow, temple dome, village huts).
- [x] **Editorial Typography**: Premium serif headings (`font-serif-heading`) paired with clean modern body typography (`Inter` / system sans).

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
