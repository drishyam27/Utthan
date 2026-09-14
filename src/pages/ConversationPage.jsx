import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, ArrowRight, ArrowLeft, CheckCircle2, Sparkles, RefreshCw, Globe, Check } from 'lucide-react';
import { speakWithSarvamAI, stopAIVoice, createSpeechRecognizer } from '../services/aiService';
import { LANGUAGES } from '../data/languages';
import { detectLanguageFromVoice } from '../data/uiTranslations';

const INTERVIEW_STEPS = [
  {
    step: 1,
    category: "workInterest",
    badge: { en: "Step 1: Trade & Skills", hi: "चरण 1: पसंदीदा काम / हुनर", bn: "ধাপ ১: পছন্দের কাজ ও দক্ষতা" },
    question: {
      en: "What kind of work or trade are you most interested in learning?",
      hi: "आप किस प्रकार के काम या हुनर में सबसे ज्यादा रुचि रखते हैं?",
      bn: "আপনি কোন ধরনের কাজ বা হস্তশিল্প শিখতে সবচেয়ে বেশি আগ্রহী?",
      ta: "நீங்கள் எந்த வகையான வேலை அல்லது திறன்களைக் கற்றுக்கொள்ள விரும்புகிறீர்கள்?",
      te: "మీరు ఏ రకమైన పని లేదా నైపుణ్యాలను నేర్చుకోవడానికి ఆసక్తి కలిగి ఉన్నారు?",
      mr: "तुम्हाला कोणत्या प्रकारच्या कामात किंवा कौशल्यात सर्वात जास्त रस आहे?",
      gu: "તમને કયા પ્રકારના કામ અથવા કૌશલ્યમાં સૌથી વધુ રસ છે?",
      kn: "ನೀವು ಯಾವ ರೀತಿಯ ಕೆಲಸ ಅಥವಾ ಕೌಶಲ್ಯವನ್ನು ಕಲಿಯಲು ಆಸಕ್ತಿ ಹೊಂದಿದ್ದೀರಿ?",
      ml: "ഏതുതരം തൊഴിലോ നൈപുണ്യമോ പഠിക്കാനാണ് കൂടുതൽ താൽപ്പര്യം?",
      pa: "ਤੁਸੀਂ ਕਿਸ ਤਰ੍ਹਾਂ ਦੇ ਕੰਮ ਜਾਂ ਹੁਨਰ ਨੂੰ ਸਿੱਖਣ ਵਿੱਚ ਸਭ ਤੋਂ ਵੱਧ ਦਿਲਚਸਪੀ ਰੱਖਦੇ ਹੋ?",
      or: "ଆପଣ କେଉଁ ପ୍ରକାରର କାମ ବା ଦକ୍ଷତା ଶିଖିବାକୁ ଅଧିକ ଆଗ୍ରହୀ?",
      as: "আপুনি কি ধৰণৰ কাম বা দক্ষতা শিকিবলৈ আটাইতকৈ বেছি আগ্ৰহী?",
      ur: "آپ کس قسم کے کام یا ہنر کو سیکھنے میں سب سے زیادہ دلچسپی رکھتے ہیں؟"
    },
    options: {
      en: ["☀️ Solar & Electrical Maintenance", "🧵 Tailoring & Handloom Weaving", "🌾 Agri-Tech & Drone Farming", "🩺 Healthcare Assistant (GDA)", "🚗 Driving & Auto Mechanics"],
      hi: ["☀️ सोलर एवं इलेक्ट्रीशियन", "🧵 सिलाई एवं हथकरघा बुनाई", "🌾 आधुनिक कृषि एवं ड्रोन पायलट", "🩺 स्वास्थ्य सहायक (GDA)", "🚗 ड्राइविंग एवं मोटर मैकेनिक"],
      bn: ["☀️ সোলার প্যানেল ও ইলেকট্রিশিয়ান", "🧵 সেলাই ও তাঁতশিল্প", "🌾 আধুনিক কৃষি ও কিষাণ ড্রোন", "🩺 স্বাস্থ্য সহকারী (GDA)", "🚗 ড্রাইভিং ও অটোমোবাইল মেকানিক"]
    }
  },
  {
    step: 2,
    category: "education",
    badge: { en: "Step 2: Education & Experience", hi: "चरण 2: शिक्षा और अनुभव", bn: "ধাপ ২: শিক্ষাগত যোগ্যতা ও অভিজ্ঞতা" },
    question: {
      en: "What is your highest education level or existing experience?",
      hi: "आपकी उच्चतम शिक्षा क्या है या पहले से कोई अनुभव है?",
      bn: "আপনার শিক্ষাগত যোগ্যতা কত দূর বা কোনো পূর্ব অভিজ্ঞতা আছে কি?",
      ta: "உங்கள் கல்வித் தகுதி அல்லது முந்தைய அனுபவம் என்ன?",
      te: "మీ అత్యున్నత విద్య లేదా మునుపటి అనుభవం ఏమిటి?",
      mr: "तुमचे शिक्षण काय आहे किंवा पूर्वीचा काही अनुभव आहे का?",
      gu: "તમારું શિક્ષણ કેટલું છે અથવા અગાઉનો કોઈ અનુભવ છે?",
      kn: "ನಿಮ್ಮ ಶಿಕ್ಷಣ ಅಥವಾ ಹಿಂದಿನ ಅನುಭವವೇನು?",
      ml: "നിങ്ങളുടെ വിദ്യാഭ്യാസ യോഗ്യതയോ മുൻപരിചയമോ എന്താണ്?",
      pa: "ਤੁਹਾਡੀ ਪੜ੍ਹਾਈ ਜਾਂ ਪਿਛਲਾ ਤਜਰਬਾ ਕੀ ਹੈ?",
      or: "ଆପଣଙ୍କ ଶିକ୍ଷାଗତ ଯୋଗ୍ୟତା ବା ପୂର୍ବ ଅଭିଜ୍ଞତା କଣ?",
      as: "আপোনাৰ শিক্ষাগত অৰ্হতা বা পূৰ্ব অভিজ্ঞতা কি?",
      ur: "آپ کی تعلیمی قابلیت یا سابقہ تجربہ کیا ہے؟"
    },
    options: {
      en: ["🎓 10th Pass", "📚 12th Pass", "🏫 8th Pass or Below", "🛠️ ITI / Vocational Diploma", "🌱 No formal schooling (Eager to learn)"],
      hi: ["🎓 10वीं पास", "📚 12वीं पास", "🏫 8वीं पास या उससे कम", "🛠️ आईटीआई / वोकेशनल डिप्लोमा", "🌱 अनौपचारिक शिक्षा (सीखने के इच्छुक)"],
      bn: ["🎓 ১০ম শ্রেণী (মাধ্যমিক) পাস", "📚 ১২ম শ্রেণী (উচ্চমাধ্যমিক) পাস", "🏫 ৮ম শ্রেণী বা তার নিচে", "🛠️ আইটিআই বা ভোকেশনাল ডিপ্লোমা", "🌱 প্রাতিষ্ঠানিক পড়াশোনা নেই (শিখতে আগ্রহী)"]
    }
  },
  {
    step: 3,
    category: "mobility",
    badge: { en: "Step 3: Location & Travel", hi: "चरण 3: कार्यस्थल और दूरी", bn: "ধাপ ৩: কাজের স্থান ও যাতায়াত" },
    question: {
      en: "How far are you comfortable traveling daily for training or work?",
      hi: "ट्रेनिंग या काम के लिए आप रोज़ कितनी दूर तक जा सकते हैं?",
      bn: "প্রশিক্ষণ বা কাজের জন্য আপনি প্রতিদিন কত দূর পর্যন্ত যাতায়াত করতে পারবেন?",
      ta: "பயிற்சி அல்லது வேலைக்காக தினமும் எவ்வளவு தூரம் பயணிக்க முடியும்?",
      te: "శిక్షణ లేదా పని కోసం మీరు ప్రతిరోజూ ఎంత దూరం ప్రయాణించగలరు?",
      mr: "प्रशिक्षण किंवा कामासाठी तुम्ही रोज किती प्रवास करू शकता?",
      gu: "તાલીમ અથવા કામ માટે તમે દરરોજ કેટલા દૂર જઈ શકો છો?",
      kn: "ತರಬೇತಿ ಅಥವಾ ಕೆಲಸಕ್ಕಾಗಿ ಪ್ರತಿದಿನ ಎಷ್ಟು ದೂರ ಪ್ರಯಾಣಿಸಲು ಸಿದ್ಧರಿದ್ದೀರಿ?",
      ml: "പരിശീലനത്തിനോ ജോലിക്കോ ദിവസേന എത്ര ദൂരം യാത്ര ചെയ്യാൻ കഴിയും?",
      pa: "ਸਿਖਲਾਈ ਜਾਂ ਕੰਮ ਲਈ ਤੁਸੀਂ ਰੋਜ਼ਾਨਾ ਕਿੰਨੀ ਦੂਰ ਜਾ ਸਕਦੇ ਹੋ?",
      or: "ପ୍ରଶିକ୍ଷଣ ବା କାମ ପାଇଁ ଆପଣ ଦୈନିକ କେତେ ଦୂର ଯାତ୍ରା କରିପାରିବେ?",
      as: "প্ৰশিক্ষণ বা কামৰ বাবে আপুনি দৈনিক কিমান দূৰলৈ যাব পাৰিব?",
      ur: "تربیت یا کام کے لیے آپ روزانہ کتنی دور سفر کر سکتے ہیں؟"
    },
    options: {
      en: ["🏡 Within my own village / block", "🚲 Up to 15 km (Nearby Market / Town)", "🚌 Anywhere in my district", "🎒 Willing to relocate if hostel provided"],
      hi: ["🏡 अपने गाँव या ब्लॉक के अंदर", "🚲 15 किमी तक (नजदीकी कस्बा)", "🚌 अपने पूरे जिले में कहीं भी", "🎒 रहने की सुविधा हो तो बाहर जाने को तैयार"],
      bn: ["🏡 নিজের গ্রাম বা ব্লকের মধ্যে", "🚲 ১৫ কিমি পর্যন্ত (কাছের শহর)", "🚌 জেলার যেকোনো জায়গায়", "🎒 হোস্টেল ও থাকার ব্যবস্থা থাকলে বাইরে যেতে প্রস্তুত"]
    }
  },
  {
    step: 4,
    category: "preference",
    badge: { en: "Step 4: Your Goal", hi: "चरण 4: आपका मुख्य लक्ष्य", bn: "ধাপ ৪: আপনার মূল লক্ষ্য" },
    question: {
      en: "What is your main goal right now?",
      hi: "इस समय आपका सबसे मुख्य लक्ष्य क्या है?",
      bn: "এই মুহূর্তে আপনার প্রধান লক্ষ্য কোনটি?",
      ta: "தற்போது உங்கள் முதன்மை இலக்கு என்ன?",
      te: "ప్రస్తుతం మీ ముఖ్య లక్ష్యం ఏమిటి?",
      mr: "सध्या तुमचे मुख्य ध्येय काय आहे?",
      gu: "આ સમયે તમારો મુખ્ય ધ્યેય શું છે?",
      kn: "ಈ ಸಮಯದಲ್ಲಿ ನಿಮ್ಮ ಮುಖ್ಯ ಗುರಿ ಏನು?",
      ml: "ഇപ്പോൾ നിങ്ങളുടെ പ്രധാന ലക്ഷ്യം എന്താണ്?",
      pa: "ਇਸ ਵੇਲੇ ਤੁਹਾਡਾ ਮੁੱਖ ਟੀਚਾ ਕੀ ਹੈ?",
      or: "ବର୍ତ୍ତମାନ ଆପଣଙ୍କ ମୁଖ୍ୟ ଲକ୍ଷ୍ୟ କଣ?",
      as: "এই মুহূৰ্তত আপোনাৰ মূল লক্ষ্য কি?",
      ur: "اس وقت آپ کا بنیادی مقصد کیا ہے؟"
    },
    options: {
      en: ["📜 Certified Training + Monthly Stipend", "💼 Immediate Local Job Placement", "🏪 Start My Own Micro-Business / Shop"],
      hi: ["📜 प्रमाणित सरकारी ट्रेनिंग + मासिक वजीफा", "💼 नजदीकी क्षेत्र में तुरंत पक्की नौकरी", "🏪 अपनी खुद की दुकान या व्यवसाय शुरू करना"],
      bn: ["📜 সার্টিফিকেট প্রশিক্ষণ + মাসিক বৃত্তি (Stipend)", "💼 এলাকায় দ্রুত চাকরির সুযোগ", "🏪 নিজের ছোট দোকান বা স্বনির্ভর ব্যবসা শুরু করা"]
    }
  }
];

export default function ConversationPage({ 
  currentLanguage, 
  onSelectLanguage,
  onCompleteConversation,
  onNavigate 
}) {
  // 0 = Language Step, 1 = Trade, 2 = Education, 3 = Travel, 4 = Goal, 5 = Complete
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState('');
  const [soundEnabled, setSoundEnabled] = useState(true);
  // Track last spoken step to prevent re-speaking on re-renders or language updates
  const lastSpokenStepRef = useRef(-1);
  const hasSpokenGreetingRef = useRef(false);
  const activeRecognizer = useRef(null);

  const langCode = currentLanguage?.id || 'en';
  const isLanguageStep = currentStepIndex === 0;
  const isCompleteStep = currentStepIndex > INTERVIEW_STEPS.length;
  const currentInterviewStep = !isLanguageStep && !isCompleteStep 
    ? INTERVIEW_STEPS[currentStepIndex - 1] 
    : null;

  // Speak when step changes to a new step
  useEffect(() => {
    if (!soundEnabled || isCompleteStep) return;

    // Prevent speaking the same step again on re-render
    if (lastSpokenStepRef.current === currentStepIndex) return;

    let textToSpeak = "";
    let speechLang = langCode;

    if (isLanguageStep) {
      if (hasSpokenGreetingRef.current) return;
      hasSpokenGreetingRef.current = true;
      textToSpeak = "Welcome to Utthan. Please speak or select your language to begin.";
      speechLang = 'en';
    } else if (currentInterviewStep) {
      textToSpeak = currentInterviewStep.question[langCode] || currentInterviewStep.question.hi || currentInterviewStep.question.en;
    }

    if (textToSpeak) {
      lastSpokenStepRef.current = currentStepIndex;
      stopAIVoice();
      setIsSpeaking(true);
      speakWithSarvamAI({
        text: textToSpeak,
        languageId: speechLang,
        speaker: 'priya'
      }).finally(() => {
        setIsSpeaking(false);
      });
    }

    return () => {
      stopAIVoice();
    };
  }, [currentStepIndex, soundEnabled]);

  // Handle language confirmation (voice or tap)
  const handleConfirmLanguage = (lang) => {
    stopAIVoice();
    if (activeRecognizer.current) {
      try { activeRecognizer.current.stop(); } catch (e) {}
    }
    setIsListening(false);
    setLiveTranscript('');

    if (onSelectLanguage) {
      onSelectLanguage(lang);
    }

    // Confirmation voice in that exact language
    const confirmationVoice = lang.id === 'bn' 
      ? "বাংলা ভাষা নির্বাচন করা হয়েছে। এবার আপনার পছন্দের কাজ সম্পর্কে জানা যাক।" 
      : lang.id === 'hi' 
        ? "हिन्दी भाषा चुनी गई है। चलिए अब आपके पसंदीदा काम के बारे में जानते हैं।" 
        : `${lang.name} language selected. Let's explore your skills.`;

    if (soundEnabled) {
      setIsSpeaking(true);
      speakWithSarvamAI({ text: confirmationVoice, languageId: lang.id, speaker: 'priya' })
        .finally(() => {
          setIsSpeaking(false);
          // Advance to Step 1 only after confirmation voice finishes
          setTimeout(() => {
            setCurrentStepIndex(1);
          }, 300);
        });
    } else {
      setCurrentStepIndex(1);
    }
  };

  // Handle answering interview steps
  const handleSelectAnswer = (selectedText) => {
    stopAIVoice();
    if (activeRecognizer.current) {
      try { activeRecognizer.current.stop(); } catch (e) {}
    }
    setIsListening(false);
    setLiveTranscript('');

    const newAnswers = { ...answers, [currentInterviewStep.category]: selectedText };
    setAnswers(newAnswers);

    if (currentStepIndex < INTERVIEW_STEPS.length) {
      // Advance to next step directly; useEffect will cleanly speak the new question
      setCurrentStepIndex(prev => prev + 1);
    } else {
      // Complete!
      setCurrentStepIndex(INTERVIEW_STEPS.length + 1);
      const completionVoice = langCode === 'bn'
        ? "অভিনন্দন! আপনার তথ্যের ভিত্তিতে আমরা আপনার জেলার ৫টি সেরা সরকারি সুযোগ খুঁজে পেয়েছি।"
        : langCode === 'hi'
          ? "बधाई हो! आपकी जानकारी के आधार पर हमने आपके जिले में सबसे उपयुक्त 5 सरकारी योजनाएं तैयार कर ली हैं।"
          : "Congratulations! Based on your answers, we have matched 5 certified government schemes in your district.";

      if (soundEnabled) {
        setIsSpeaking(true);
        speakWithSarvamAI({ text: completionVoice, languageId: langCode, speaker: 'priya' })
          .finally(() => setIsSpeaking(false));
      }
    }
  };

  // Voice recording
  const startVoiceInput = () => {
    stopAIVoice();
    setLiveTranscript('');

    const recognizer = createSpeechRecognizer({
      languageId: isLanguageStep ? 'en' : langCode,
      onResult: (transcript, isFinal) => {
        setLiveTranscript(transcript);

        if (isLanguageStep) {
          // Detect spoken language
          const detected = detectLanguageFromVoice(transcript, LANGUAGES);
          if (detected) {
            setIsListening(false);
            handleConfirmLanguage(detected);
          }
        } else {
          // Regular interview answer
          if (isFinal && transcript.trim()) {
            setIsListening(false);
            handleSelectAnswer(transcript);
          }
        }
      },
      onError: (err) => {
        console.warn("Speech error:", err);
        setIsListening(false);
      },
      onEnd: () => {
        setIsListening(false);
      }
    });

    if (recognizer) {
      try {
        recognizer.start();
        setIsListening(true);
        activeRecognizer.current = recognizer;
      } catch (e) {
        setIsListening(false);
      }
    } else {
      setIsListening(false);
    }
  };

  const stopVoiceInput = () => {
    if (activeRecognizer.current) {
      try { activeRecognizer.current.stop(); } catch (e) {}
    }
    setIsListening(false);
    if (liveTranscript.trim()) {
      if (isLanguageStep) {
        const detected = detectLanguageFromVoice(liveTranscript, LANGUAGES);
        if (detected) {
          handleConfirmLanguage(detected);
        }
      } else {
        handleSelectAnswer(liveTranscript);
      }
    }
  };

  const handleReplayQuestion = () => {
    if (isSpeaking) {
      // Toggle off if currently speaking
      stopAIVoice();
      setIsSpeaking(false);
      return;
    }

    let text = "";
    let speechLang = langCode;
    if (isLanguageStep) {
      text = "Welcome to Utthan. Please speak or select your language to begin.";
      speechLang = 'en';
    } else if (currentInterviewStep) {
      text = currentInterviewStep.question[langCode] || currentInterviewStep.question.hi || currentInterviewStep.question.en;
    }

    if (text) {
      stopAIVoice();
      setIsSpeaking(true);
      speakWithSarvamAI({ text, languageId: speechLang, speaker: 'priya' }).finally(() => {
        setIsSpeaking(false);
      });
    }
  };

  return (
    <div className="relative z-20 flex-1 flex flex-col items-center justify-center max-w-3xl mx-auto w-full px-4 sm:px-6 py-6 min-h-[calc(100vh-140px)]">
      
      {/* ============================================================ */}
      {/* 1. STEP 0: AI TAKES INPUT OF PREFERRED LANGUAGE BY VOICE/TAP */}
      {/* ============================================================ */}
      {isLanguageStep && (
        <div className="bg-white/95 backdrop-blur-md rounded-3xl p-6 sm:p-8 border-2 border-[#134e40]/30 shadow-xl text-center max-w-xl w-full animate-in fade-in duration-300">
          
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-xs font-bold text-[#134e40] bg-[#FAF7F0] px-3.5 py-1.5 rounded-full border border-[#b8ded6]">
              <Globe className="w-3.5 h-3.5 text-[#134e40]" />
              <span>Step 0: Choose / Speak Language</span>
            </div>

            <button
              onClick={handleReplayQuestion}
              className={`p-2 rounded-full border border-[#b8ded6] hover:bg-[#FAF7F0] text-[#134e40] transition-colors ${
                isSpeaking ? 'bg-emerald-100 animate-pulse ring-2 ring-emerald-400' : 'bg-white'
              }`}
              title="Re-listen voice greeting"
            >
              <Volume2 className="w-4 h-4" />
            </button>
          </div>

          <h2 className="font-serif-heading text-2xl sm:text-3xl font-bold text-[#134e40] mb-2">
            Speak or Select Your Language
          </h2>
          <p className="text-xs sm:text-sm text-[#37474F] mb-6">
            Say your language aloud (e.g. <span className="font-bold text-[#134e40]">"বাংলা"</span>, <span className="font-bold text-[#134e40]">"हिन्दी"</span>, <span className="font-bold text-[#134e40]">"English"</span>) or tap an option below.
          </p>

          {/* Central Voice Button for Language */}
          <div className="mb-6 flex flex-col items-center">
            <button
              onClick={isListening ? stopVoiceInput : startVoiceInput}
              className={`relative group w-20 h-20 sm:w-24 sm:h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl active:scale-95 focus:outline-none ${
                isListening 
                  ? 'bg-red-600 text-white animate-pulse ring-4 ring-red-300' 
                  : 'bg-[#134e40] text-white hover:bg-[#0d3b30] hover:scale-105'
              }`}
              title="Tap and say your language"
            >
              {isListening && (
                <>
                  <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-75" />
                  <span className="absolute -inset-2 rounded-full border-2 border-red-500 animate-pulse opacity-50" />
                </>
              )}
              <Mic className="w-8 h-8 sm:w-10 sm:h-10 relative z-10" />
            </button>

            <span className="mt-3 text-xs sm:text-sm font-semibold text-[#134e40]">
              {isListening 
                ? (liveTranscript ? `Hearing: "${liveTranscript}"...` : "Listening... Say 'বাংলা', 'Hindi', 'Tamil'...")
                : isSpeaking 
                  ? "Speaking greeting aloud (Sarvam AI)..."
                  : "Tap to Speak your language"}
            </span>
          </div>

          {/* 22 Language Cards Grid */}
          <div className="text-left w-full">
            <span className="text-[11px] font-bold text-[#718078] uppercase tracking-wider block mb-2 text-center">
              Or Tap to Select (22 Indian Languages + English)
            </span>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-56 overflow-y-auto p-1">
              {LANGUAGES.map((l) => (
                <button
                  key={l.id}
                  onClick={() => handleConfirmLanguage(l)}
                  className={`p-2.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                    currentLanguage?.id === l.id 
                      ? 'bg-white border-[#134e40] ring-2 ring-[#134e40]/20 font-bold' 
                      : 'bg-white/80 hover:bg-[#134e40] hover:text-white border-[#cbd5e1] text-[#263238]'
                  }`}
                >
                  <span className="text-sm">{l.nativeName}</span>
                  <span className="text-[10px] text-gray-400">{l.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 2. STEPS 1-4: STEP-BY-STEP VOICE ASSISTANT INTERVIEW        */}
      {/* ============================================================ */}
      {!isLanguageStep && !isCompleteStep && currentInterviewStep && (
        <div className="bg-white/95 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-[#b8ded6] shadow-xl max-w-2xl w-full flex flex-col items-center text-center transition-all animate-in fade-in duration-300">
          
          {/* Top Step Pill & Voice Controls */}
          <div className="w-full flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-xs font-bold text-[#134e40] bg-[#FAF7F0] px-3.5 py-1.5 rounded-full border border-[#b8ded6]">
              <Sparkles className="w-3.5 h-3.5 text-[#e69943]" />
              <span>{currentInterviewStep.badge[langCode] || currentInterviewStep.badge.hi || currentInterviewStep.badge.en}</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  if (soundEnabled) stopAIVoice();
                  setSoundEnabled(!soundEnabled);
                }}
                className={`p-2 rounded-full border transition-colors ${
                  soundEnabled ? 'bg-[#134e40] text-white border-[#134e40]' : 'bg-white text-[#718078] border-[#cbd5e1]'
                }`}
                title={soundEnabled ? "Audio ON" : "Audio Muted"}
              >
                {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              </button>

              <button
                onClick={handleReplayQuestion}
                className={`p-2 rounded-full border border-[#b8ded6] hover:bg-[#FAF7F0] text-[#134e40] transition-colors ${
                  isSpeaking ? 'bg-emerald-100 animate-pulse ring-2 ring-emerald-400' : 'bg-white'
                }`}
                title="Re-listen question"
              >
                <Volume2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden mb-6 border border-[#b8ded6]/40">
            <div 
              className="bg-[#134e40] h-full transition-all duration-500 rounded-full"
              style={{ width: `${(currentStepIndex / INTERVIEW_STEPS.length) * 100}%` }}
            />
          </div>

          {/* Question Heading in Preferred Language */}
          <h2 className="font-serif-heading text-2xl sm:text-3xl md:text-4xl font-bold text-[#134e40] leading-snug mb-6 max-w-xl">
            {currentInterviewStep.question[langCode] || currentInterviewStep.question.hi || currentInterviewStep.question.en}
          </h2>

          {/* Center Voice Mic Button */}
          <div className="mb-6 flex flex-col items-center">
            <button
              onClick={isListening ? stopVoiceInput : startVoiceInput}
              className={`relative group w-20 h-20 sm:w-24 sm:h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl active:scale-95 focus:outline-none ${
                isListening 
                  ? 'bg-red-600 text-white animate-pulse ring-4 ring-red-300' 
                  : 'bg-[#134e40] text-white hover:bg-[#0d3b30] hover:scale-105'
              }`}
              title="Tap to Speak your answer"
            >
              {isListening && (
                <>
                  <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-75" />
                  <span className="absolute -inset-2 rounded-full border-2 border-red-500 animate-pulse opacity-50" />
                </>
              )}
              <Mic className="w-8 h-8 sm:w-10 sm:h-10 relative z-10" />
            </button>

            <span className="mt-3 text-xs sm:text-sm font-semibold text-[#134e40]">
              {isListening 
                ? (liveTranscript ? `"${liveTranscript}"` : `Listening in ${currentLanguage.nativeName}... Speak now!`)
                : isSpeaking 
                  ? "Speaking question aloud (Sarvam AI)..."
                  : "Tap to Speak your answer"}
            </span>
          </div>

          {/* Option Cards */}
          <div className="w-full">
            <div className="flex items-center justify-center gap-2 mb-3">
              <span className="h-px bg-gray-200 flex-1" />
              <span className="text-[11px] font-bold text-[#718078] uppercase tracking-wider">
                Or Tap an Option
              </span>
              <span className="h-px bg-gray-200 flex-1" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
              {(currentInterviewStep.options[langCode] || currentInterviewStep.options.hi || currentInterviewStep.options.en).map((opt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectAnswer(opt)}
                  className="p-3 sm:p-3.5 rounded-2xl bg-white hover:bg-[#134e40] text-[#134e40] hover:text-white border border-[#b8ded6] hover:border-[#134e40] text-xs sm:text-sm font-semibold text-left transition-all shadow-sm hover:shadow-md active:scale-98 flex items-center justify-between group"
                >
                  <span>{opt}</span>
                  <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all shrink-0 ml-2" />
                </button>
              ))}
            </div>
          </div>

          {/* Bottom Back Button */}
          <div className="w-full flex items-center justify-between mt-6 pt-4 border-t border-gray-100 text-xs text-[#718078]">
            <button
              onClick={() => {
                stopAIVoice();
                setCurrentStepIndex(prev => Math.max(0, prev - 1));
              }}
              className="flex items-center gap-1 hover:text-[#134e40] font-medium"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>
            <span className="font-semibold">Step {currentStepIndex} of {INTERVIEW_STEPS.length}</span>
          </div>

        </div>
      )}

      {/* ============================================================ */}
      {/* 3. COMPLETION SCREEN: SUMMARY & MATCHED SCHEMES             */}
      {/* ============================================================ */}
      {isCompleteStep && (
        <div className="bg-white/95 backdrop-blur-md rounded-3xl p-6 sm:p-8 border-2 border-[#134e40]/30 shadow-xl text-center max-w-xl w-full animate-in fade-in zoom-in-95 duration-400">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-[#134e40] flex items-center justify-center mx-auto mb-4 border border-emerald-300 shadow-sm">
            <CheckCircle2 className="w-9 h-9" />
          </div>

          <h2 className="font-serif-heading text-2xl sm:text-3xl font-bold text-[#134e40] mb-2">
            {langCode === 'bn' ? 'আপনার প্রোফাইল প্রস্তুত হয়েছে!' : langCode === 'hi' ? 'आपकी प्रोफ़ाइल तैयार है!' : 'Your Pathway is Ready!'}
          </h2>

          <p className="text-sm sm:text-base text-[#37474F] mb-6">
            {langCode === 'bn' 
              ? 'আপনার দেওয়া তথ্যের ভিত্তিতে আমরা আপনার জন্য সরকারি প্রশিক্ষণ ও মাসিক বৃত্তির সুযোগ প্রস্তুত করেছি।' 
              : langCode === 'hi' 
                ? 'आपकी जानकारी के आधार पर सरकारी योजनाओं एवं वजीफे वाले काम के अवसर तैयार हैं।'
                : 'Based on your voice answers, we have matched 5 verified government-certified opportunities for you.'}
          </p>

          {/* User Answers Summary */}
          <div className="bg-[#FAF7F0] rounded-2xl p-4 border border-[#b8ded6] mb-6 text-left space-y-2 text-xs sm:text-sm">
            <div className="flex items-center justify-between">
              <span className="text-[#718078]">Language:</span>
              <span className="font-bold text-[#134e40]">{currentLanguage.nativeName} ({currentLanguage.name})</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#718078]">Trade / Interest:</span>
              <span className="font-bold text-[#134e40]">{answers.workInterest || "Selected"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#718078]">Education:</span>
              <span className="font-bold text-[#134e40]">{answers.education || "Selected"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#718078]">Location:</span>
              <span className="font-bold text-[#134e40]">{answers.mobility || "Selected"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#718078]">Goal:</span>
              <span className="font-bold text-[#134e40]">{answers.preference || "Selected"}</span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => onCompleteConversation(answers)}
              className="px-6 py-3.5 rounded-full bg-[#134e40] hover:bg-[#0d3b30] text-white font-bold text-sm sm:text-base shadow-lg active:scale-95 transition-all flex items-center justify-center gap-2"
            >
              <span>View Matched Opportunities (5)</span>
              <ArrowRight className="w-5 h-5" />
            </button>

            <button
              onClick={() => {
                stopAIVoice();
                setCurrentStepIndex(0);
                setAnswers({});
              }}
              className="px-5 py-3 rounded-full border border-[#cbd5e1] hover:bg-white text-[#718078] font-medium text-sm transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Start Over</span>
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
