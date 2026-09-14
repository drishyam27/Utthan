/**
 * Utthan AI & Multilingual Voice Service
 * Integrates:
 * 1. Groq API (High-speed Llama / Qwen inference) for intelligent livelihood advice
 * 2. Sarvam AI API (Bulbul:v3 Indic TTS) for natural Indian language voice playback
 * 3. Web Speech Recognition API for real microphone speech-to-text
 */

const GROQ_API_KEY = import.meta.env.VITE_GROQ_API_KEY || '';
const SARVAM_API_KEY = import.meta.env.VITE_SARVAM_API_KEY || '';

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
 * Generate intelligent livelihood advice using Groq
 */
export async function askUtthanAI({ prompt, language, conversationHistory = [] }) {
  const languageName = language?.name || 'Hindi';
  const languageNative = language?.nativeName || 'हिन्दी';

  const systemMessage = {
    role: 'system',
    content: `You are Utthan (उत्थान), an empathetic, deeply knowledgeable AI livelihood and opportunity advisor for Indian citizens, especially rural artisans, youth, women, and unorganized workers.
Your mission is to guide them toward verified government schemes (PMKVY 4.0, PM Vishwakarma, DDU-GKY, Lakhpati Didi, National Rural Livelihood Mission, NABARD), certified vocational courses, free tools/stipends, and local employment pathways.

Rules:
1. Always respond in the user's chosen language: ${languageName} (${languageNative}).
2. Keep your answer warm, inspiring, concise, and easy to understand (2 to 4 sentences maximum).
3. Mention practical benefits like monthly stipends, toolkits, certificates, or training centers.
4. Do NOT include thought processes, markdown code fences, or XML tags like <think>. Provide pure conversational response only.`
  };

  const messages = [
    systemMessage,
    ...conversationHistory.slice(-4).map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text
    })),
    { role: 'user', content: prompt }
  ];

  try {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'qwen/qwen3.6-27b',
        messages: messages,
        temperature: 0.6,
        max_tokens: 300
      })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err?.error?.message || `Groq request failed (${response.status})`);
    }

    const data = await response.json();
    let reply = data?.choices?.[0]?.message?.content || '';

    // Clean any <think> blocks that might be returned by reasoning models
    reply = reply.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();

    return reply;
  } catch (error) {
    console.error('Groq AI Error:', error);
    // Fallback response in user's language
    if (language?.id === 'hi') {
      return "उत्थान आपकी सहायता के लिए तैयार है। आपके क्षेत्र में सोलर पैनल, सिलाई एवं कृषि ड्रोन जैसी कई सरकारी योजनाएं और वजीफे उपलब्ध हैं।";
    }
    return `Utthan is here to support you. There are certified skill training programs and monthly stipends available in your district for your skills.`;
  }
}

/**
 * Text-to-Speech using Sarvam AI Bulbul:v3 with fallback to Web Speech API
 */
export async function speakWithSarvamAI({ text, languageId = 'hi', speaker = 'priya' }) {
  stopAIVoice();

  // Strip Markdown or special characters for clean pronunciation
  const cleanText = text.replace(/[*_#`~[\]()]/g, '').trim();
  if (!cleanText) return false;

  // Track session ID for this specific utterance to prevent any concurrent speech
  const sessionId = ++currentSpeechSessionId;
  const controller = new AbortController();
  activeAbortController = controller;

  const targetLangCode = SARVAM_LANG_MAP[languageId];

  // If language is supported by Sarvam AI, use Sarvam Bulbul Indic Voice
  if (targetLangCode && SARVAM_API_KEY) {
    try {
      const res = await fetch('https://api.sarvam.ai/text-to-speech', {
        method: 'POST',
        signal: controller.signal,
        headers: {
          'api-subscription-key': SARVAM_API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          inputs: [cleanText.slice(0, 450)], // Keep within comfortable sentence chunk
          target_language_code: targetLangCode,
          speaker: speaker,
          pitch: 0,
          pace: 1.0,
          loudness: 1.5,
          speech_sample_rate: 22050
        })
      });

      // Discard if another speech was initiated while network fetch was running
      if (sessionId !== currentSpeechSessionId) {
        return false;
      }

      if (res.ok) {
        const data = await res.json();
        if (sessionId !== currentSpeechSessionId) {
          return false;
        }

        if (data.audios && data.audios[0]) {
          const audioSrc = `data:audio/wav;base64,${data.audios[0]}`;
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
              resolve(false);
            };
            audio.play().catch(() => resolve(false));
          });
        }
      } else {
        console.warn('Sarvam TTS returned status:', res.status);
      }
    } catch (sarvamErr) {
      if (sarvamErr.name === 'AbortError') {
        return false; // Stopped cleanly
      }
      console.warn('Sarvam TTS error:', sarvamErr);
    }
  }

  // Discard if another speech was initiated
  if (sessionId !== currentSpeechSessionId) {
    return false;
  }

  // Fallback: Browser Web Speech API
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = targetLangCode ? targetLangCode.replace('-', '_') : 'hi-IN';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
      return true;
    } catch (e) {
      console.error('SpeechSynthesis error:', e);
    }
  }

  return false;
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
