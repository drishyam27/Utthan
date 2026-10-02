import assert from 'node:assert/strict';
import { isAudioRecordingSupported, AudioRecorder } from '../src/services/audioRecorder.js';

function matchTranscriptToOption(transcript, options) {
  if (!transcript || !Array.isArray(options) || options.length === 0) return null;
  const clean = transcript.toLowerCase().trim();

  const directMatch = options.find(opt => opt.toLowerCase().trim() === clean);
  if (directMatch) return directMatch;

  const stripEmojis = (str) => str.replace(/[\p{Emoji}\p{Extended_Pictographic}]/gu, '').toLowerCase().trim();
  const cleanStripped = stripEmojis(transcript);

  const emojiStrippedMatch = options.find(opt => stripEmojis(opt) === cleanStripped);
  if (emojiStrippedMatch) return emojiStrippedMatch;

  const substringMatch = options.find(opt => {
    const stripped = stripEmojis(opt);
    return cleanStripped.includes(stripped) || (stripped.length > 5 && stripped.includes(cleanStripped));
  });
  if (substringMatch) return substringMatch;

  const words = cleanStripped.split(/[\s,()/-]+/).filter(w => w.length >= 3);
  for (const opt of options) {
    const optWords = stripEmojis(opt).split(/[\s,()/-]+/).filter(w => w.length >= 3);
    for (const word of words) {
      if (optWords.some(ow => ow.includes(word) || word.includes(ow))) {
        return opt;
      }
    }
  }

  return null;
}

// 1. Audio recording support check in node environment
assert.equal(isAudioRecordingSupported(), false, 'Node environment should report false for audio recording');

// 2. AudioRecorder class initialization
const recorder = new AudioRecorder({ maxDurationMs: 15000 });
assert.equal(recorder.state, 'idle');
assert.equal(recorder.maxDurationMs, 15000);

// 3. Option matching tests with multilingual transcripts
const tradeOptionsHi = [
  "☀️ सोलर एवं इलेक्ट्रीशियन",
  "🧵 सिलाई एवं हथकरघा बुनाई",
  "🌾 आधुनिक कृषि एवं ड्रोन पायलट",
  "🩺 स्वास्थ्य सहायक (GDA)",
  "🚗 ड्राइविंग एवं मोटर मैकेनिक",
];

const tradeOptionsBn = [
  "☀️ সোলার প্যানেল ও ইলেকট্রিশিয়ান",
  "🧵 সেলাই ও তাঁতশিল্প",
  "🌾 আধুনিক কৃষি ও কিষাণ ড্রোন",
  "🩺 স্বাস্থ্য সহকারী (GDA)",
  "🚗 ড্রাইভিং ও অটোমোবাইল মেকানিক",
];

const educationOptionsHi = [
  "🎓 10वीं पास",
  "📚 12वीं पास",
  "🏫 8वीं पास या उससे कम",
  "🛠️ आईटीआई / वोकेशनल डिप्लोमा",
  "🌱 अनौपचारिक शिक्षा (सीखने के इच्छुक)",
];

// Test direct match without emoji
assert.equal(
  matchTranscriptToOption("सिलाई एवं हथकरघा बुनाई", tradeOptionsHi),
  "🧵 सिलाई एवं हथकरघा बुनाई",
  "Should match exact Hindi trade text without emoji"
);

// Test keyword match for "सिलाई" (Tailoring)
assert.equal(
  matchTranscriptToOption("मुझे सिलाई सीखना है", tradeOptionsHi),
  "🧵 सिलाई एवं हथकरघा बुनाई",
  "Should match Hindi keyword 'सिलाई'"
);

// Test Bengali keyword match for "ড্রোন" (Drone)
assert.equal(
  matchTranscriptToOption("আমি কিষাণ ড্রোন চালাতে চাই", tradeOptionsBn),
  "🌾 আধুনিক কৃষি ও কিষাণ ড্রোন",
  "Should match Bengali keyword 'ড্রোন'"
);

// Test Education match for "10वीं"
assert.equal(
  matchTranscriptToOption("मैंने 10वीं पास की है", educationOptionsHi),
  "🎓 10वीं पास",
  "Should match Hindi education keyword '10वीं'"
);

// Test non-matching transcript
assert.equal(
  matchTranscriptToOption("अंतरिक्ष यात्री बनना चाहता हूँ", tradeOptionsHi),
  null,
  "Should return null for unrelated transcript"
);

console.log('✓ multilingual voice integration frontend tests passed');
