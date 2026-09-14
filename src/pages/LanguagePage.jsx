import React, { useState, useRef } from 'react';
import { LANGUAGES } from '../data/languages';
import { Check, Globe, ArrowLeft, Sparkles, Search, Mic, Volume2 } from 'lucide-react';
import { createSpeechRecognizer, speakWithSarvamAI, stopAIVoice } from '../services/aiService';
import { detectLanguageFromVoice } from '../data/uiTranslations';

export default function LanguagePage({ 
  currentLanguage, 
  onSelectLanguage, 
  onBack,
  isModal = false 
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isListeningVoice, setIsListeningVoice] = useState(false);
  const [voiceDetectedText, setVoiceDetectedText] = useState('');
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const activeRecognizer = useRef(null);

  const filteredLanguages = LANGUAGES.filter((lang) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      lang.name.toLowerCase().includes(q) ||
      lang.nativeName.toLowerCase().includes(q) ||
      lang.script.toLowerCase().includes(q)
    );
  });

  const startVoiceLanguageSelection = () => {
    stopAIVoice();
    setVoiceDetectedText('');
    setDetectedLanguage(null);
    setIsListeningVoice(true);

    const recognizer = createSpeechRecognizer({
      languageId: 'en', // Multi-accent English / Indic recognition
      onResult: (transcript, isFinal) => {
        setVoiceDetectedText(transcript);
        const match = detectLanguageFromVoice(transcript, LANGUAGES);
        if (match) {
          setDetectedLanguage(match);
          if (isFinal) {
            confirmAndSelectLanguage(match);
          }
        }
      },
      onError: (err) => {
        console.warn("Language speech error:", err);
        setIsListeningVoice(false);
      },
      onEnd: () => {
        setIsListeningVoice(false);
      }
    });

    if (recognizer) {
      try {
        recognizer.start();
        activeRecognizer.current = recognizer;
      } catch (e) {
        setIsListeningVoice(false);
      }
    } else {
      setIsListeningVoice(false);
    }
  };

  const stopVoiceLanguageSelection = () => {
    if (activeRecognizer.current) {
      try { activeRecognizer.current.stop(); } catch (e) {}
    }
    setIsListeningVoice(false);
    if (detectedLanguage) {
      confirmAndSelectLanguage(detectedLanguage);
    }
  };

  const confirmAndSelectLanguage = (lang) => {
    setIsListeningVoice(false);
    // Announce confirmation with Sarvam AI voice
    const confirmationText = lang.id === 'bn' 
      ? "বাংলা ভাষা নির্বাচন করা হয়েছে।" 
      : lang.id === 'hi' 
        ? "हिन्दी भाषा चुनी गई है।" 
        : `${lang.name} language selected.`;

    speakWithSarvamAI({ text: confirmationText, languageId: lang.id, speaker: 'priya' });

    setTimeout(() => {
      onSelectLanguage(lang);
    }, 600);
  };

  return (
    <div className={`relative z-20 flex-1 flex flex-col items-center ${isModal ? 'p-5 sm:p-6 max-h-[88vh] overflow-y-auto' : 'px-4 sm:px-6 lg:px-12 py-8 max-w-5xl mx-auto'}`}>
      {/* Header */}
      <div className="w-full flex items-center justify-between mb-5 pb-3 border-b border-[#b8ded6]/60">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium text-[#134e40] hover:text-[#0d3b30] p-1.5 -ml-1 rounded-lg hover:bg-white/60 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>

        <div className="flex items-center gap-2 text-[#134e40] bg-white/80 px-3 py-1 rounded-full border border-[#b8ded6]/70 shadow-sm">
          <Globe className="w-4 h-4 text-[#134e40]" />
          <span className="text-xs uppercase tracking-wider font-semibold">22 Indian Languages + English</span>
        </div>
      </div>

      {/* Main Heading */}
      <div className="text-center mb-5">
        <h1 className="font-serif-heading text-2xl sm:text-3xl lg:text-4xl font-bold text-[#134e40] mb-2">
          Choose or Speak Your Language
        </h1>
        <p className="text-xs sm:text-sm text-[#37474F] max-w-lg mx-auto">
          Say your language name aloud or tap an option below. The entire application and voice assistant will immediately adapt to your choice.
        </p>
      </div>

      {/* 🎙️ Voice Language Input Section */}
      <div className="w-full max-w-xl mb-6 bg-white/95 rounded-2xl p-4 sm:p-5 border-2 border-[#134e40]/30 shadow-md flex flex-col items-center text-center">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#134e40] mb-2">
          <Sparkles className="w-4 h-4 text-[#e69943]" />
          <span>Voice Language Selector (বলুন বা বলুন)</span>
        </div>

        <button
          onClick={isListeningVoice ? stopVoiceLanguageSelection : startVoiceLanguageSelection}
          className={`relative group px-6 py-3 rounded-full flex items-center gap-3 transition-all duration-300 shadow-md active:scale-95 mb-2 ${
            isListeningVoice 
              ? 'bg-red-600 text-white animate-pulse ring-4 ring-red-200' 
              : 'bg-[#134e40] text-white hover:bg-[#0d3b30]'
          }`}
        >
          <Mic className={`w-5 h-5 ${isListeningVoice ? 'animate-bounce' : ''}`} />
          <span className="text-sm font-semibold">
            {isListeningVoice ? "Listening... Say your language!" : "Tap to Speak Language (e.g. 'বাংলা' or 'Hindi')"}
          </span>
        </button>

        {/* Live speech recognition feedback */}
        {isListeningVoice && (
          <p className="text-xs font-medium text-[#134e40] animate-pulse">
            {voiceDetectedText ? `Hearing: "${voiceDetectedText}"...` : "Say 'Bengali', 'Hindi', 'Tamil', 'English', 'Odia', etc..."}
          </p>
        )}

        {detectedLanguage && !isListeningVoice && (
          <div className="mt-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300 animate-in fade-in">
            ✓ Recognized: {detectedLanguage.nativeName} ({detectedLanguage.name})
          </div>
        )}

        {/* Quick Voice/Tap Shortcuts */}
        <div className="mt-3 flex flex-wrap justify-center items-center gap-1.5 text-xs">
          <span className="text-[#718078] text-[11px]">Quick picks:</span>
          {['bn', 'hi', 'en', 'ta', 'te', 'mr', 'gu', 'or'].map((code) => {
            const l = LANGUAGES.find(item => item.id === code);
            if (!l) return null;
            return (
              <button
                key={code}
                onClick={() => confirmAndSelectLanguage(l)}
                className="px-2.5 py-1 rounded-lg bg-[#FAF7F0] hover:bg-[#134e40] text-[#134e40] hover:text-white border border-[#b8ded6] text-xs font-medium transition-colors"
              >
                {l.nativeName}
              </button>
            );
          })}
        </div>
      </div>

      {/* Search Bar */}
      <div className="w-full max-w-md mb-5 relative">
        <Search className="w-4 h-4 text-[#718078] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by name or script (e.g. বাংলা, हिन्दी, Tamil)..."
          className="w-full pl-10 pr-4 py-2 bg-white/90 border border-[#b8ded6] rounded-xl text-xs sm:text-sm text-[#263238] placeholder-[#718078] focus:outline-none focus:ring-2 focus:ring-[#134e40]/30 shadow-sm"
        />
      </div>

      {/* Language Grid (All 23 Languages) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 sm:gap-3 w-full">
        {filteredLanguages.map((lang) => {
          const isSelected = currentLanguage.id === lang.id;
          return (
            <button
              key={lang.id}
              onClick={() => confirmAndSelectLanguage(lang)}
              className={`p-3 sm:p-3.5 rounded-xl text-left border transition-all flex items-center justify-between group active:scale-98 ${
                isSelected
                  ? 'bg-white border-[#134e40] shadow-md ring-2 ring-[#134e40]/20'
                  : 'bg-white/85 hover:bg-white border-[#cbd5e1] hover:border-[#134e40]/50 shadow-sm'
              }`}
            >
              <div className="flex flex-col">
                <span className="text-lg sm:text-xl font-bold text-[#134e40]">
                  {lang.nativeName}
                </span>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-xs text-[#718078] font-medium">
                    {lang.name}
                  </span>
                  <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.2 rounded bg-[#FAF7F0] border border-[#cbd5e1]/60 text-[#52796f]">
                    {lang.script}
                  </span>
                </div>
              </div>

              <div className={`w-6 h-6 rounded-full flex items-center justify-center border transition-colors ${
                isSelected 
                  ? 'bg-[#134e40] border-[#134e40] text-white' 
                  : 'border-[#cbd5e1] group-hover:border-[#134e40]/40'
              }`}>
                {isSelected && <Check className="w-3.5 h-3.5" />}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
