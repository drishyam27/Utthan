import React from 'react';

/**
 * VoiceButton Component
 * Faithfully matches the concentric ring microphone interaction button from the references.
 * Features deep forest green center, white microphone icon, "Tap to Speak" label,
 * and concentric translucent waves.
 */
export default function VoiceButton({ 
  state = 'idle', // 'idle' | 'listening' | 'processing'
  onClick, 
  label = 'Tap to Speak',
  className = '' 
}) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* 1. Outermost Concentric Ring */}
      <div 
        className={`absolute rounded-full pointer-events-none transition-all duration-700 ${
          state === 'listening' 
            ? 'w-72 h-72 sm:w-80 sm:h-80 lg:w-96 lg:h-96 bg-[#134e40]/[0.05] animate-wave-3' 
            : state === 'processing'
            ? 'w-64 h-64 sm:w-72 sm:h-72 lg:w-88 lg:h-88 bg-[#e69943]/[0.08] animate-pulse'
            : 'w-64 h-64 sm:w-72 sm:h-72 lg:w-84 lg:h-84 bg-[#134e40]/[0.035]'
        }`}
      />

      {/* 2. Middle Concentric Ring */}
      <div 
        className={`absolute rounded-full pointer-events-none transition-all duration-500 ${
          state === 'listening' 
            ? 'w-56 h-56 sm:w-64 sm:h-64 lg:w-76 lg:h-76 bg-[#134e40]/[0.08] animate-wave-2' 
            : state === 'processing'
            ? 'w-52 h-52 sm:w-60 sm:h-60 lg:w-70 lg:h-70 bg-[#e69943]/[0.12] animate-pulse'
            : 'w-52 h-52 sm:w-60 sm:h-60 lg:w-68 lg:h-68 bg-[#134e40]/[0.06]'
        }`}
      />

      {/* 3. Inner Subtle Ring */}
      <div 
        className={`absolute rounded-full pointer-events-none transition-all duration-300 ${
          state === 'listening' 
            ? 'w-44 h-44 sm:w-50 sm:h-50 lg:w-58 lg:h-58 bg-[#134e40]/[0.12] animate-wave-1' 
            : state === 'processing'
            ? 'w-40 h-40 sm:w-46 sm:h-46 lg:w-52 lg:h-52 bg-[#e69943]/[0.16]'
            : 'w-40 h-40 sm:w-46 sm:h-46 lg:w-52 lg:h-52 bg-[#134e40]/[0.09]'
        }`}
      />

      {/* 4. Primary Core Deep Forest Green Circular Button */}
      <button
        onClick={onClick}
        className={`relative z-10 w-32 h-32 sm:w-36 sm:h-36 lg:w-40 lg:h-40 rounded-full flex flex-col items-center justify-center text-white transition-all duration-300 cursor-pointer shadow-lg active:scale-95 focus:outline-none focus:ring-4 focus:ring-[#134e40]/20 ${
          state === 'listening'
            ? 'bg-[#0d3b30] scale-105 ring-4 ring-[#80c2b2]/40'
            : state === 'processing'
            ? 'bg-[#185648] scale-100'
            : 'bg-[#134e40] hover:bg-[#0f4437] hover:scale-[1.02]'
        }`}
        aria-label={label}
      >
        {/* State-dependent Visual Indicator */}
        {state === 'listening' ? (
          <div className="flex flex-col items-center">
            {/* Live soundwave animation */}
            <div className="flex items-center gap-1.5 h-10 mb-2">
              <span className="w-1 bg-white rounded-full h-4 animate-[bounce_0.8s_infinite_100ms]"></span>
              <span className="w-1 bg-white rounded-full h-8 animate-[bounce_0.8s_infinite_200ms]"></span>
              <span className="w-1 bg-white rounded-full h-10 animate-[bounce_0.8s_infinite_300ms]"></span>
              <span className="w-1 bg-white rounded-full h-7 animate-[bounce_0.8s_infinite_400ms]"></span>
              <span className="w-1 bg-white rounded-full h-4 animate-[bounce_0.8s_infinite_500ms]"></span>
            </div>
            <span className="text-xs sm:text-[13px] font-medium tracking-wide text-white/95">
              Listening...
            </span>
          </div>
        ) : state === 'processing' ? (
          <div className="flex flex-col items-center">
            {/* Soft breathing spinner */}
            <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin mb-2" />
            <span className="text-xs sm:text-[13px] font-medium tracking-wide text-white/95">
              Understanding...
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center select-none">
            {/* Microphone Icon matching the reference line art */}
            <svg 
              className="w-10 h-10 sm:w-11 sm:h-11 mb-2 text-white" 
              viewBox="0 0 40 40" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2.4" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              {/* Mic capsule */}
              <rect x="14" y="6" width="12" height="18" rx="6" fill="currentColor" />
              {/* Subtle friendly face / sound cleft dots */}
              <circle cx="17.5" cy="13" r="1" fill="#134e40" stroke="none" />
              <circle cx="22.5" cy="13" r="1" fill="#134e40" stroke="none" />
              <path d="M 18 17 Q 20 19 22 17" stroke="#134e40" strokeWidth="1.2" fill="none" />

              {/* Surrounding sound pickup cradle */}
              <path d="M 9 17 C 9 24.5, 15 28, 20 28 C 25 28, 31 24.5, 31 17" stroke="currentColor" strokeWidth="2.5" fill="none" />
              {/* Stem and base */}
              <line x1="20" y1="28" x2="20" y2="34" stroke="currentColor" strokeWidth="2.5" />
              <line x1="13" y1="34" x2="27" y2="34" stroke="currentColor" strokeWidth="2.5" />
            </svg>

            {/* Label below microphone */}
            <span className="text-xs sm:text-[13px] font-medium tracking-normal text-white/95">
              {label}
            </span>
          </div>
        )}
      </button>
    </div>
  );
}
