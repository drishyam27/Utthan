# Phase 3E — Conversational Voice Loop & Multilingual TTS Architecture

## 1. Overview & Data Flow

Utthan implements an end-to-end multilingual conversational loop that connects voice speech, speech recognition, deterministic normalization, structured interview state machine, NSQF recommendation engine 2.0, natural-language explanation, and text-to-speech.

```text
Beneficiary speaks
        ↓
Sarvam STT (saaras:v4) [POST /api/voice/transcribe]
        ↓
Transcript
        ↓
Deterministic Option Matcher (Fast Path)
        │
   ┌────┴────────────────────────┐
   │ Exact match                 │ Natural language / Ambiguous
   ▼                             ▼
Structured Answer       Groq Interpretation [POST /api/adaptive-interview/{id}/interpret]
   │                             │
   │                             ▼
   │                    (Clarification / Contradiction Loop)
   │                             │
   └─────────────┬───────────────┘
                 ↓
      Phase 3B Normalization
                 ↓
  Structured Beneficiary Profile
                 ↓
  Adaptive Interview State Machine
                 ↓
           Next Question
                 ↓
   Sarvam TTS [POST /api/voice/synthesize] (Bulbul:v3)
                 ↓
      Beneficiary hears question
                 ↓
               LOOP
                 ↓
         Interview COMPLETE
                 ↓
   Recommendation Engine 2.0 (Authoritative NSQF/NQR Catalog)
                 ↓
   Real NSQF Qualifications & Match Reasons
                 ↓
   Groq Conversational Explanation [POST /api/adaptive-interview/{id}/explain-recommendations]
                 ↓
   Sarvam TTS [POST /api/voice/synthesize]
                 ↓
   Beneficiary hears explanation & reads on-screen
```

---

## 2. Architectural Boundaries & Provider Responsibilities

| Subsystem | Component | Responsibility | Boundary Constraints |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text (STT)** | Sarvam AI `saaras:v4` | Audio binary $\to$ text transcript | Backend proxy; zero client credential exposure; rejects empty audio; does not interpret semantics. |
| **Option Matcher** | Deterministic Matcher | Exact label, synonym & canonical token mapping | Bypasses LLM for known options (10th, 12th, ITI, yes/no, etc.). |
| **Conversational Parser** | Groq Llama / Qwen | Conversational dialect $\to$ structured profile fields | Detects ambiguity and contradictions; **never** picks courses; **never** alters catalog eligibility. |
| **Interview State Machine** | Phase 3B Engine | Tracks stage, generates adaptive questions, calculates completeness | Authoritative progression rules; immutable completed sessions. |
| **Recommendation Engine** | Phase 3D Engine 2.0 | Hard eligibility evaluation & explainable ranking | Live NSQF database catalog only; deterministic scoring; transparent failure reasons. |
| **Recommendation Explanation** | Groq Llama | Deterministic match reasons $\to$ spoken language explanation | Strictly grounded in catalog metadata and match reasons; cannot alter courses or ranks. |
| **Text-to-Speech (TTS)** | Sarvam AI `Bulbul:v3` | Assistant text $\to$ natural Indic voice audio | Backend proxy (`POST /api/voice/synthesize`); zero client credential exposure; graceful Web Speech fallback. |

---

## 3. Multilingual Coverage & Graceful Degradation

### Supported Languages:
- **Sarvam STT (`saaras:v4`)**: Supports all 22 Eighth Schedule Indian languages.
- **Sarvam TTS (`Bulbul:v3`)**: Supports 11 Indian languages natively:
  - Hindi (`hi-IN`)
  - Bengali (`bn-IN`)
  - Telugu (`te-IN`)
  - Tamil (`ta-IN`)
  - Marathi (`mr-IN`)
  - Gujarati (`gu-IN`)
  - Kannada (`kn-IN`)
  - Malayalam (`ml-IN`)
  - Odia (`od-IN`)
  - Punjabi (`pa-IN`)
  - Indian English (`en-IN`)
- **Other Eighth Schedule Languages (Urdu, Assamese, Dogri, etc.)**:
  - The backend returns `fallback_needed=True` with no errors.
  - The frontend automatically routes playback through the browser's native Web Speech API (`SpeechSynthesis`).

### Voice Failure Fallback Principle:
1. **Audio Recording / Mic Denied**: Citizen is alerted with an accessible text banner; text input and clickable options remain fully interactive.
2. **STT Timeout or Unintelligible**: Clear error message displayed on-screen; allows instant retry or tapping manual options.
3. **TTS Offline / Provider Failure**: The question or explanation is always rendered as readable text on screen; synthesis failure never halts or breaks the interview.
4. **Groq Offline / Provider Failure**: Deterministic multilingual templates immediately take over for recommendation explanations; deterministic canonical matcher handles interview steps.

---

## 4. Security & Privacy Guarantees

1. **Zero Client Secret Exposure**:
   - `SARVAM_API_KEY` and `GROQ_API_KEY` are stored strictly on the FastAPI backend.
   - Frontend clients make authenticated calls to `/api/voice/synthesize` and `/api/voice/transcribe`.
2. **Anonymous Capability Tokens**:
   - Every beneficiary session is guarded by a high-entropy capability token.
   - Cross-user session access and cross-user recommendation explanations are rejected with `401 Unauthorized` or `403 Forbidden`.
3. **Audio Privacy**:
   - Raw audio recordings and voice buffers are processed in memory and never persisted to the database.
   - Speech synthesis returns ephemeral Base64 audio for playback only.
