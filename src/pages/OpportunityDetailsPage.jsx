import React from 'react';
import { 
  ArrowLeft, CheckCircle2, AlertCircle, Award, 
  MapPin, Calendar, IndianRupee, ArrowRight, ShieldCheck, Sparkles 
} from 'lucide-react';
import { getUIText } from '../data/uiTranslations';

export default function OpportunityDetailsPage({ 
  currentLanguage,
  opportunity, 
  onBack, 
  onStartActionPath 
}) {
  if (!opportunity) return null;
  const langId = currentLanguage?.id || 'en';

  return (
    <div className="relative z-20 flex-1 px-4 sm:px-6 lg:px-12 py-8 max-w-4xl mx-auto w-full">
      {/* Back button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm font-medium text-[#134e40] hover:text-[#0d3b30] mb-6 p-1.5 -ml-1 rounded-lg hover:bg-white/60 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>{getUIText('details', 'backToOpps', langId)}</span>
      </button>

      {/* Main Banner Card */}
      <div className="bg-white/95 rounded-3xl p-6 sm:p-8 border border-[#b8ded6] shadow-sm mb-8">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300">
            ★ {opportunity.matchScore}% {getUIText('details', 'matchBadge', langId)}
          </span>
          <span className="text-xs font-medium text-[#718078] bg-[#FAF7F0] px-3 py-1 rounded-full border border-[#cbd5e1]">
            {opportunity.category}
          </span>
          <span className="text-xs text-[#134e40] font-semibold">
            {opportunity.partner}
          </span>
        </div>

        <h1 className="font-serif-heading text-3xl sm:text-4xl font-bold text-[#134e40] mb-3">
          {opportunity.title}
        </h1>

        <p className="text-base text-[#37474F] leading-relaxed mb-6">
          {opportunity.overview}
        </p>

        {/* Quick Spec Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-[#b8ded6]/60">
          <div>
            <span className="text-xs text-[#718078] uppercase tracking-wider block mb-1">
              {getUIText('details', 'durationFormat', langId)}
            </span>
            <span className="text-sm font-bold text-[#134e40]">{opportunity.duration}</span>
          </div>
          <div>
            <span className="text-xs text-[#718078] uppercase tracking-wider block mb-1">
              {getUIText('details', 'stipendSupport', langId)}
            </span>
            <span className="text-sm font-bold text-emerald-700">{opportunity.stipend}</span>
          </div>
          <div>
            <span className="text-xs text-[#718078] uppercase tracking-wider block mb-1">
              {getUIText('details', 'expectedIncome', langId)}
            </span>
            <span className="text-sm font-bold text-[#134e40]">{opportunity.avgEarnings}</span>
          </div>
        </div>
      </div>

      {/* Skill Gap Analysis Section (Core requirement) */}
      <div className="bg-white/95 rounded-3xl p-6 sm:p-8 border border-[#b8ded6] shadow-sm mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-5 h-5 text-[#e69943]" />
          <h2 className="text-xl sm:text-2xl font-bold text-[#134e40]">
            Visual Skill Gap Analysis
          </h2>
        </div>
        <p className="text-sm text-[#718078] mb-6">
          Utthan AI compares your current abilities against what this opportunity requires. You only need to learn the missing skills!
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Skills Possessed */}
          <div className="p-5 rounded-2xl bg-[#DCECDF]/50 border border-[#b8ded6]">
            <div className="flex items-center gap-2 text-[#134e40] font-bold text-sm mb-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <span>{getUIText('details', 'skillsYouHave', langId)} ({opportunity.skillsPossessed.length})</span>
            </div>
            <ul className="space-y-2 text-sm text-[#263238]">
              {opportunity.skillsPossessed.map((skill, i) => (
                <li key={i} className="flex items-center gap-2 bg-white/80 p-2.5 rounded-xl border border-[#b8ded6]/40">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="font-medium">{skill}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Skills Missing (Actionable learning targets) */}
          <div className="p-5 rounded-2xl bg-[#FFF8EE] border border-[#FAD7AB]">
            <div className="flex items-center gap-2 text-[#9e4c16] font-bold text-sm mb-3">
              <AlertCircle className="w-5 h-5 text-[#e69943]" />
              <span>{getUIText('details', 'skillsYouWillLearn', langId)} ({opportunity.skillsMissing.length})</span>
            </div>
            <ul className="space-y-2 text-sm text-[#263238]">
              {opportunity.skillsMissing.map((skill, i) => (
                <li key={i} className="flex items-center gap-2 bg-white/90 p-2.5 rounded-xl border border-[#fad7ab]/50">
                  <span className="w-2 h-2 rounded-full bg-[#e69943]" />
                  <span className="font-medium text-[#7a3b0e]">{skill}</span>
                  <span className="text-[11px] ml-auto text-[#718078] bg-[#FAF7F0] px-2 py-0.5 rounded">
                    Included in curriculum
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Eligibility Requirements */}
      <div className="bg-white/95 rounded-3xl p-6 sm:p-8 border border-[#b8ded6] shadow-sm mb-8">
        <h2 className="text-xl font-bold text-[#134e40] mb-4">
          {getUIText('details', 'eligibilityCriteria', langId)}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          {opportunity.eligibility.map((req, i) => (
            <div key={i} className="flex items-center gap-2.5 p-3 rounded-xl bg-[#FAF7F0] border border-[#cbd5e1]">
              <ShieldCheck className="w-4 h-4 text-[#134e40]" />
              <span className="text-[#37474F] font-medium">{req}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Path CTA Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-3xl bg-[#134e40] text-white shadow-lg">
        <div>
          <h3 className="text-lg font-bold">Ready to take the next step?</h3>
          <p className="text-xs sm:text-sm text-[#dbeef5]">
            Utthan will guide you step-by-step through enrollment and training completion.
          </p>
        </div>

        <button
          onClick={() => onStartActionPath(opportunity)}
          className="w-full sm:w-auto px-6 py-3 rounded-full bg-white text-[#134e40] font-bold text-sm flex items-center justify-center gap-2 hover:bg-[#dbeef5] transition-all shadow-md active:scale-95"
        >
          <span>{getUIText('details', 'startActionPath', langId)}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
