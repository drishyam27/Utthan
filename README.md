# 🇮🇳 Utthan (उत्थान)

> **AI-Powered Multilingual Public Service & Livelihood Discovery Platform for Every Indian Citizen**

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Sarvam AI](https://img.shields.io/badge/Sarvam_AI-Bulbul:v3_TTS-FF6B35)](https://www.sarvam.ai/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_Fast_Inference-F05A28)](https://groq.com/)
[![Languages](https://img.shields.io/badge/Languages-22_Scheduled_Indic_+_English-138808)](#-multilingual-matrix-23-languages)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 Overview

**Utthan (उत्थान)** is a Digital Public Goods initiative designed to bridge the gap between grassroots citizens and the vast ecosystem of Indian government welfare programs, vocational training schemes, stipends, and dignified livelihood pathways.

A large segment of India's demographic dividend—rural artisans, self-help groups (SHGs), daily wage workers, and youth in non-urban districts—faces steep digital and linguistic barriers when navigating complex government portals and bureaucratic procedures. **Utthan eliminates this friction through a voice-first, culturally authentic, and conversational AI interface available in all 22 official Eighth Schedule Indian languages plus English.**

---

## 🌟 Key Features

### 1. 🎙️ Voice-First Conversational Discovery
- **Natural Speech Interaction**: Citizens can simply speak in their mother tongue to state their trade, education, and career aspirations using the built-in browser Web Speech API.
- **High-Fidelity Indic Speech Synthesis**: Integrated with **Sarvam AI (Bulbul:v3)** to deliver natural, emotionally resonant, and dialect-accurate audio playback across Indian languages.
- **Echo & Audio Collision Prevention**: Engineered single-session speech locking (`AbortController` & session token guards) that eliminates audio overlaps and stuttering during dynamic conversations.

### 2. 🌐 22 Scheduled Indian Languages + English
- **Step 0 Language Preference**: Prominently prompts the user at the start of their journey via interactive grid or voice input (e.g., saying *"Hindi"*, *"বাংলা"*, *"தமிழ்"*, or *"తెలుగు"*).
- **Dynamic Full-Platform Localization**: Seamlessly translates all components across the user journey:
  - Navigation bar & announcements
  - Hero section & call-to-actions
  - Step-by-step interview questionnaire
  - Livelihood opportunity cards & eligibility filters
  - Detail modals, documentation guides, and footer

### 3. 🤝 Guided 4-Step Interactive Pathway
Rather than overwhelming citizens with a generic search bar, Utthan's AI guide leads users through four simple, structured steps:
1. **Trade / Craft**: Carpenter, Tailor, Electrician, Potter, Weaver, Farmer, Construction, IT/Digital, etc.
2. **Education Level**: No Formal Schooling, 5th/8th Pass, 10th/12th Matric, ITI / Diploma, Graduate.
3. **Geographic Location**: State and rural/semi-urban district preference.
4. **Immediate Goal**: Skill Certification, Toolkit Grant, Monthly Stipend, Self-Employment Loan, Direct Job Placement.

### 4. 🏛️ Integrated Government Schemes & Opportunities
Curated real-time matching with major national missions:
- **PM Vishwakarma Yojana**: ₹15,000 toolkit grants, collateral-free credit at 5%, basic/advanced stipends for 18 traditional artisan trades.
- **Pradhan Mantri Kaushal Vikas Yojana (PMKVY 4.0)**: Free industry-aligned NSQF skill certification with conveyance allowance and digital literacy training.
- **Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)**: Guaranteed wage employment training for rural youth with free boarding and lodging.
- **National Rural Livelihood Mission (NRLM / Lakhpati Didi)**: Revolving funds, micro-enterprise training, and market linkages for women self-help groups.
- **PM Matsya Sampada & Agri-Infra**: Cold-chain, fisheries, and rural agrarian enterprise schemes.

### 5. 🎨 Cultural Heritage & Glassmorphic UI
- **Authentic Folk Art Backgrounds**: Handcrafted cultural motifs depicting traditional Indian vocations (handloom weaving, pottery, agriculture, masonry, brass metalwork).
- **Calibrated Light Aesthetic**: Soft, warm cream background (`#FAF7F0`) with tuned saturation and high-contrast typography for outdoor daylight legibility on budget smartphones.
- **Mobile-First Responsive Layout**: Dedicated portrait backdrop artwork for mobile smartphones and landscape artwork for tablets/desktops.

---

## 🗺️ Multilingual Matrix (23 Languages)

| Code | Language | Native Script | Code | Language | Native Script |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `en` | English | English | `mr` | Marathi | मराठी |
| `hi` | Hindi | हिन्दी | `gu` | Gujarati | ગુજરાતી |
| `bn` | Bengali | বাংলা | `kn` | Kannada | ಕನ್ನಡ |
| `ta` | Tamil | தமிழ் | `ml` | Malayalam | മലയാളം |
| `te` | Telugu | తెలుగు | `pa` | Punjabi | ਪੰਜਾਬੀ |
| `or` | Odia | ଓଡ଼ିଆ | `as` | Assamese | অসমীয়া |
| `ur` | Urdu | اردو | `sa` | Sanskrit | संस्कृतम् |
| `ma` | Maithili | मैथिली | `ks` | Kashmiri | کٲشُر |
| `ne` | Nepali | नेपाली | `sd` | Sindhi | سنڌي |
| `kok`| Konkani | कोंकणी | `doi`| Dogri | डोगरी |
| `mni`| Manipuri | মৈতৈলোন্ | `brx`| Bodo | बड़ो |
| `sat`| Santali | ᱥᱟᱱᱛᱟᱲᱤ | - | - | - |

---

## 🏗️ Architecture & Technology Stack

```
                       ┌─────────────────────────────────────┐
                       │           Citizen Device            │
                       │   (Mobile Browser / Desktop Web)    │
                       └──────────────────┬──────────────────┘
                                          │
                   Web Speech STT / UI    │    Indic TTS Audio Playback
                                          ▼
                       ┌─────────────────────────────────────┐
                       │        Utthan React Frontend        │
                       │  (Vite + TailwindCSS + Lucide Icons)│
                       └──────┬───────────────────────┬──────┘
                              │                       │
               Prompt context │                       │ Indic Text
                              ▼                       ▼
                   ┌─────────────────────┐ ┌─────────────────────┐
                   │      Groq API       │ │    Sarvam AI API    │
                   │ (Llama 3.3 / Qwen)  │ │ (Bulbul:v3 IndicTTS)│
                   │ Fast Multi-turn LLM │ │ Neural Voice Stream │
                   └─────────────────────┘ └─────────────────────┘
```

- **Frontend Framework**: React 18 with Vite 6
- **Styling & Tokens**: Tailwind CSS with custom glassmorphism and Indian cultural color palette
- **Icons**: Lucide React
- **Reasoning Engine**: Groq Cloud Platform (`llama-3.3-70b-versatile` / `qwen-2.5-32b`)
- **Voice Synthesis Engine**: Sarvam AI API (`bulbul:v3`) with Indic phonetics
- **Localization**: Native dictionary lookups + contextual real-time fallback translation

---

## 📂 Project Structure

```
Utthan/
├── public/                     # Static cultural artwork & brand icons
│   ├── utthan-bg.jpg           # High-resolution desktop background
│   └── utthan-bg-mobile.jpg    # Tailored portrait mobile background
├── src/
│   ├── components/             # Reusable UI widgets
│   │   ├── Footer.jsx          # Cultural footer with national links
│   │   ├── LanguagePreferenceModal.jsx  # Step 0 voice & click language selector
│   │   ├── Navbar.jsx          # Header with branding, language picker & quick links
│   │   ├── OpportunityCard.jsx # Scheme card with stipends, duration & eligibility
│   │   ├── OpportunityDetailModal.jsx   # Deep-dive scheme application modal
│   │   └── VoiceAssistantModal.jsx      # Guided step-by-step interactive interview
│   ├── context/
│   │   └── LanguageContext.jsx # Global active language & translation state
│   ├── data/
│   │   ├── languages.js        # 23-language metadata, greetings & sample prompts
│   │   ├── opportunities.js    # Comprehensive repository of Indian welfare schemes
│   │   └── uiTranslations.js   # Master multilingual UI dictionary
│   ├── pages/
│   │   ├── HowToUsePage.jsx    # Visual step-by-step citizen onboarding walkthrough
│   │   ├── LandingPage.jsx     # Hero, statistics, category filters & matched schemes
│   │   └── OpportunitiesPage.jsx # Searchable, filterable catalog of all schemes
│   ├── services/
│   │   └── aiService.js        # Groq LLM & Sarvam AI voice integration service
│   ├── App.jsx                 # Routing and global modal controllers
│   ├── index.css               # Design system, glassmorphism tokens & typography
│   └── main.jsx                # Application root mount
├── .env.example                # Template for required environment variables
├── package.json                # Project dependencies & build scripts
├── tailwind.config.js          # Cultural theme, fonts, and responsive breakpoints
└── vite.config.js              # Vite server configuration with mobile host support
```

---

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (version 18.0 or higher recommended)
- `npm` or `yarn`

### 1. Clone the Repository
```bash
git clone https://github.com/drishyam27/Utthan.git
cd Utthan
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and add your API keys:
```env
# Groq API Key (Inference engine for livelihood advice)
# Free key at: https://console.groq.com/keys
VITE_GROQ_API_KEY=your_groq_api_key_here

# Sarvam AI API Key (Indic voice synthesis)
# Key at: https://www.sarvam.ai/
VITE_SARVAM_API_KEY=your_sarvam_api_key_here
```

### 4. Start the Development Server
```bash
npm run dev
```
The application will be accessible at `http://localhost:5173`.

---

## 📱 Mobile Device Testing

To test the application on a mobile smartphone with active microphone permissions:

### Option A: Cloudflare Tunnel (Recommended — No Wi-Fi restrictions)
1. Download [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/):
```powershell
.\cloudflared.exe tunnel --url http://localhost:5173
```
2. Cloudflare will output an `https://<unique-name>.trycloudflare.com` URL.
3. Open this link on your smartphone's browser (Chrome on Android, Safari on iOS).

### Option B: Local Network / Hotspot
1. Run Vite with host exposure:
```bash
npm run dev -- --host
```
2. Connect your phone and laptop to the same Wi-Fi network or mobile hotspot.
3. Navigate to `http://<your-laptop-ip>:5173` on your phone.

---

## 🛡️ Digital Public Goods Principles

Utthan is designed in alignment with the **Digital Public Goods Standard**:
- **Open Access**: Universal access regardless of literacy level or linguistic background.
- **Data Privacy**: No biometric or citizen personal data is stored without explicit user consent.
- **Lightweight Architecture**: Fast loading times even on 2G/3G connections and budget hardware.
- **Interoperability**: Built ready for direct integration with **Bhashini (National Language Translation Mission)**, **DigiLocker**, and **Skill India Digital Hub**.

---

## 🤝 Contributing

Contributions are warmly welcomed! To contribute:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/NewIndicLanguageVoice`).
3. Commit your changes (`git commit -m 'Add Dogri and Maithili dialect prompts'`).
4. Push to the branch (`git push origin feature/NewIndicLanguageVoice`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>🇮🇳 Utthan — Empowering Every Citizen's Livelihood Journey Through Voice and Technology.</b>
</p>
