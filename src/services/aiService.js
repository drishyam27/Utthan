/**
 * Utthan AI & Multilingual Voice Service
 * Integrates:
 * 1. Groq API (High-speed Llama / Qwen inference) for intelligent livelihood advice
 * 2. Sarvam AI API (Bulbul:v3 Indic TTS) for natural Indian language voice playback
 * 3. Web Speech Recognition API for real microphone speech-to-text
 */
import { synthesizeSpeech } from './api';

// Map Utthan language IDs to Sarvam AI target language codes
const SARVAM_LANG_MAP = {
  hi: 'hi-IN',
  bn: 'bn-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  mr: 'mr-IN',
  gu: 'gu-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  pa: 'pa-IN',
  or: 'od-IN',
  en: 'en-IN',
};

// Global audio player reference and cancellation tokens to guarantee only 1 voice plays at any time
let currentAudioInstance = null;
let activeAbortController = null;
let currentSpeechSessionId = 0;

/**
 * Stop any ongoing voice playback and cancel pending network requests
 */
export function stopAIVoice() {
  currentSpeechSessionId++; // Invalidate any pending in-flight audio fetches

  if (activeAbortController) {
    try {
      activeAbortController.abort();
    } catch (e) {}
    activeAbortController = null;
  }

  if (currentAudioInstance) {
    try {
      currentAudioInstance.pause();
      currentAudioInstance.currentTime = 0;
      currentAudioInstance.src = '';
    } catch (e) {
      console.warn("Could not pause audio", e);
    }
    currentAudioInstance = null;
  }

  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }
}

/**
 * Text-to-Speech using Backend Sarvam AI Bulbul:v3 proxy with fallback to Web Speech API.
 * Keeps Sarvam credentials strictly on the backend.
 */
export async function speakWithSarvamAI({ text, languageId = 'hi', speaker = 'priya' }) {
  stopAIVoice();

  // Strip Markdown or special characters for clean pronunciation
  const cleanText = (text || '').replace(/[*_#`~[\]()]/g, '').trim();
  if (!cleanText) return false;

  // Track session ID for this specific utterance to prevent any concurrent speech
  const sessionId = ++currentSpeechSessionId;
  const targetLangCode = SARVAM_LANG_MAP[languageId] || languageId;

  // Primary Path: Backend Sarvam TTS endpoint
  try {
    const res = await synthesizeSpeech(cleanText.slice(0, 450), languageId, speaker);

    // Discard if another speech was initiated while network fetch was running
    if (sessionId !== currentSpeechSessionId) {
      return false;
    }

    if (res && res.audio_base64 && !res.fallback_needed) {
      const mimeType = res.mime_type || 'audio/wav';
      const audioSrc = `data:${mimeType};base64,${res.audio_base64}`;
      const audio = new Audio(audioSrc);
      currentAudioInstance = audio;

      return new Promise((resolve) => {
        audio.onended = () => {
          if (currentAudioInstance === audio) {
            currentAudioInstance = null;
          }
          resolve(true);
        };
        audio.onerror = () => {
          if (currentAudioInstance === audio) {
            currentAudioInstance = null;
          }
          // On audio playback error, try browser speech synthesis fallback
          speakWithBrowserVoice(cleanText, targetLangCode).then(resolve);
        };
        audio.play().catch(() => {
          speakWithBrowserVoice(cleanText, targetLangCode).then(resolve);
        });
      });
    }
  } catch (err) {
    console.warn('Backend TTS synthesis proxy error, falling back to browser speech:', err);
  }

  // Discard if another speech was initiated
  if (sessionId !== currentSpeechSessionId) {
    return false;
  }

  // Secondary Fallback: Browser Web Speech API
  return speakWithBrowserVoice(cleanText, targetLangCode);
}

/**
 * Fallback browser Web Speech Synthesis helper
 */
function speakWithBrowserVoice(text, langCode) {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return Promise.resolve(false);
  }

  return new Promise((resolve) => {
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = langCode ? langCode.replace('-', '_') : 'hi-IN';
      utterance.rate = 0.95;
      utterance.onend = () => resolve(true);
      utterance.onerror = () => resolve(false);
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('Browser SpeechSynthesis error:', e);
      resolve(false);
    }
  });
}

/**
 * Real Web Speech Recognition hook
 */
export function createSpeechRecognizer({ languageId = 'hi', onResult, onError, onEnd }) {
  if (typeof window === 'undefined') return null;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('SpeechRecognition not supported in this browser.');
    return null;
  }

  const recognition = new SpeechRecognition();
  const langMap = {
    en: 'en-IN',
    hi: 'hi-IN',
    bn: 'bn-IN',
    ta: 'ta-IN',
    te: 'te-IN',
    mr: 'mr-IN',
    gu: 'gu-IN',
    kn: 'kn-IN',
    ml: 'ml-IN',
    pa: 'pa-IN',
    or: 'or-IN',
    as: 'as-IN',
    ur: 'ur-IN',
  };

  recognition.lang = langMap[languageId] || 'hi-IN';
  recognition.interimResults = true;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    let interimTranscript = '';
    let finalTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }

    const transcript = finalTranscript || interimTranscript;
    if (onResult && transcript) {
      onResult(transcript, !!finalTranscript);
    }
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    if (onError) onError(event.error);
  };

  recognition.onend = () => {
    if (onEnd) onEnd();
  };

  return recognition;
}
