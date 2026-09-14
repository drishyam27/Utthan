import React from 'react';

/**
 * CulturalBackground Component
 * Implements the exact desktop and mobile background artwork provided by the user:
 * - Desktop (>= 768px): utthan-bg.jpg (horizontal landscape format)
 * - Mobile (< 768px): utthan-bg-mobile.jpg (portrait mobile format)
 */
export default function CulturalBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none select-none z-0 overflow-hidden bg-[#FAF7F0]">
      {/* Desktop Background (>= 768px) */}
      <img
        src="/assets/utthan-bg.jpg"
        alt="Utthan Indian Cultural Desktop Background"
        className="hidden md:block w-full h-full object-cover object-center pointer-events-none select-none opacity-50 filter brightness-[1.20] saturate-[0.70] contrast-[0.90]"
      />

      {/* Mobile Background (< 768px) */}
      <img
        src="/assets/utthan-bg-mobile.jpg"
        alt="Utthan Indian Cultural Mobile Background"
        className="block md:hidden w-full h-full object-cover object-top pointer-events-none select-none opacity-50 filter brightness-[1.22] saturate-[0.70] contrast-[0.90]"
      />

      {/* Soft Light Mode Ambient Washes for optimal readability and pastel aesthetic */}
      <div className="absolute inset-0 bg-[#FAF7F0]/35 pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(255,255,255,0.85)_0%,_rgba(255,255,255,0.40)_60%,_rgba(250,247,240,0.15)_100%)] pointer-events-none" />
    </div>
  );
}
