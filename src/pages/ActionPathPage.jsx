import React, { useState } from 'react';
import { CheckCircle2, Circle, Clock, ArrowRight, Award, Sparkles, MapPin, PhoneCall } from 'lucide-react';
import { MOCK_OPPORTUNITIES } from '../data/mockOpportunities';

export default function ActionPathPage({ opportunity = MOCK_OPPORTUNITIES[0], onNavigate }) {
  const [steps, setSteps] = useState(opportunity?.actionSteps || MOCK_OPPORTUNITIES[0].actionSteps);

  const toggleStep = (index) => {
    const updated = [...steps];
    if (updated[index].status === 'completed') {
      updated[index].status = 'current';
    } else {
      updated[index].status = 'completed';
    }
    setSteps(updated);
  };

  return (
    <div className="relative z-20 flex-1 px-4 sm:px-6 lg:px-12 py-8 max-w-3xl mx-auto w-full">
      {/* 1. Header Banner */}
      <div className="text-center mb-8">
        <span className="px-3.5 py-1 rounded-full bg-[#134e40]/10 text-[#134e40] text-xs font-semibold uppercase tracking-wider inline-flex items-center gap-1.5 mb-2">
          <Sparkles className="w-3.5 h-3.5 text-[#e69943]" />
          Personalized Career Pathway
        </span>
        <h1 className="font-serif-heading text-3xl sm:text-4xl lg:text-5xl font-bold text-[#134e40] mb-2">
          Your Action Roadmap
        </h1>
        <p className="text-sm sm:text-base text-[#37474F] max-w-xl mx-auto">
          Pathway to become a certified <strong>{opportunity?.title || 'Solar Rooftop Technician'}</strong>. Follow these simple milestones at your own pace.
        </p>
      </div>

      {/* 2. Visual Timeline Pathway */}
      <div className="bg-white/95 rounded-3xl p-6 sm:p-8 border border-[#b8ded6] shadow-sm mb-8">
        <div className="relative pl-6 sm:pl-8 border-l-2 border-[#134e40]/30 space-y-8 my-2">
          {steps.map((item, index) => {
            const isCompleted = item.status === 'completed';
            const isCurrent = item.status === 'current';

            return (
              <div key={item.step} className="relative group">
                {/* Step indicator node on the timeline */}
                <button
                  onClick={() => toggleStep(index)}
                  className={`absolute -left-[35px] sm:-left-[43px] top-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center border-2 transition-all cursor-pointer shadow-sm ${
                    isCompleted
                      ? 'bg-[#134e40] border-[#134e40] text-white'
                      : isCurrent
                      ? 'bg-amber-100 border-[#e69943] text-[#e69943] ring-4 ring-amber-100/60'
                      : 'bg-white border-[#cbd5e1] text-[#718078]'
                  }`}
                  title="Click to toggle status"
                  aria-label={`Step ${item.step} status`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : isCurrent ? (
                    <Clock className="w-5 h-5 animate-pulse" />
                  ) : (
                    <span className="text-xs sm:text-sm font-bold">{item.step}</span>
                  )}
                </button>

                {/* Step Content */}
                <div className={`p-4 sm:p-5 rounded-2xl border transition-all ${
                  isCurrent 
                    ? 'bg-[#FAF7F0] border-[#134e40]/40 shadow-md ring-1 ring-[#134e40]/10' 
                    : isCompleted
                    ? 'bg-white/70 border-[#b8ded6]/70'
                    : 'bg-white/40 border-[#cbd5e1]/60 opacity-80'
                }`}>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className={`text-xs uppercase tracking-wider font-bold ${
                      isCompleted ? 'text-emerald-700' : isCurrent ? 'text-[#e69943]' : 'text-[#718078]'
                    }`}>
                      {isCompleted ? '✓ Completed' : isCurrent ? '● In Progress (You Are Here)' : `Upcoming Step ${item.step}`}
                    </span>
                    <span className="text-xs text-[#718078]">Step {item.step}</span>
                  </div>

                  <h3 className="text-base sm:text-lg font-bold text-[#134e40] mb-1">
                    {item.title}
                  </h3>

                  <p className="text-xs sm:text-sm text-[#37474F] leading-relaxed">
                    {item.desc}
                  </p>

                  {isCurrent && (
                    <div className="mt-3 pt-3 border-t border-[#b8ded6]/60 flex items-center justify-between">
                      <span className="text-xs text-[#134e40] font-medium flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5" /> Nearest Center: Varanasi ITI Campus
                      </span>
                      <button
                        onClick={() => toggleStep(index)}
                        className="px-3 py-1 bg-[#134e40] text-white rounded-full text-xs font-semibold hover:bg-[#0d3b30]"
                      >
                        Mark Completed
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Support & Helpline Card */}
      <div className="bg-[#FAF7F0] rounded-2xl p-5 border border-[#b8ded6] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 text-left">
          <div className="p-3 rounded-full bg-[#134e40] text-white shrink-0">
            <PhoneCall className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#134e40]">Need Help with Verification or Enrollment?</h4>
            <p className="text-xs text-[#718078]">Toll-Free Kisan & Artisan Mitra Helpline: 1800-180-1551</p>
          </div>
        </div>

        <button
          onClick={() => onNavigate('opportunities')}
          className="px-4 py-2 rounded-full border border-[#134e40] text-[#134e40] text-xs sm:text-sm font-semibold hover:bg-white transition-colors shrink-0"
        >
          Explore Other Pathways
        </button>
      </div>
    </div>
  );
}
