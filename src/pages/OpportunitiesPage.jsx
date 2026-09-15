import React, { useEffect, useState } from 'react';
import { fetchOpportunities, ApiError } from '../services/api';
import { mapOpportunity } from '../services/opportunityAdapter';
import { Sparkles, MapPin, ArrowRight, Filter } from 'lucide-react';
import { getUIText } from '../data/uiTranslations';

export default function OpportunitiesPage({ 
  currentLanguage,
  stateId,
  onSelectOpportunity
}) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retryToken, setRetryToken] = useState(0);
  const langId = currentLanguage?.id || 'en';

  const categories = ['All', 'Green Energy', 'Traditional Craft', 'Agri-Tech', 'Healthcare', 'Dairy'];

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');

    fetchOpportunities({ stateId })
      .then((payload) => {
        if (!cancelled) setOpportunities((payload.opportunities || []).map(mapOpportunity));
      })
      .catch((requestError) => {
        if (!cancelled) {
          setError(requestError instanceof ApiError ? requestError.message : 'Opportunities could not be loaded.');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [stateId, retryToken]);

  const filtered = selectedCategory === 'All'
    ? opportunities
    : opportunities.filter(o => o.category.toLowerCase().includes(selectedCategory.toLowerCase()));

  return (
    <div className="relative z-20 flex-1 px-4 sm:px-6 lg:px-12 py-8 max-w-5xl mx-auto w-full">
      {/* 1. Header Banner */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-3 py-1 rounded-full bg-[#134e40]/10 text-[#134e40] text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#e69943]" />
            {getUIText('opportunities', 'aiVerified', langId)}
          </span>
          <span className="text-xs text-[#718078]">
            {getUIText('opportunities', 'updatedRegion', langId)}
          </span>
        </div>
        <h1 className="font-serif-heading text-3xl sm:text-4xl lg:text-5xl font-bold text-[#134e40] mb-2">
          {getUIText('opportunities', 'pageTitle', langId)}
        </h1>
        <p className="text-sm sm:text-base text-[#37474F] max-w-2xl">
          {getUIText('opportunities', 'pageSubtitle', langId)}
        </p>
      </div>

      {loading && (
        <div className="bg-white/95 rounded-2xl p-6 border border-[#b8ded6] text-sm text-[#718078]">
          Loading verified opportunities...
        </div>
      )}

      {!loading && error && (
        <div className="bg-white/95 rounded-2xl p-6 border border-[#FAD7AB] text-sm text-[#7a3b0e] flex items-center justify-between gap-4">
          <span>{error}</span>
          <button onClick={() => setRetryToken((token) => token + 1)} className="font-bold text-[#134e40] hover:underline whitespace-nowrap">
            Retry from the page
          </button>
        </div>
      )}

      {/* 2. Category Filter Pills */}
      {!loading && !error && <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-6 scrollbar-none">
        <span className="text-xs font-semibold text-[#718078] uppercase tracking-wider flex items-center gap-1 mr-1 shrink-0">
          <Filter className="w-3.5 h-3.5" /> {getUIText('opportunities', 'filterSector', langId)}
        </span>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all whitespace-nowrap active:scale-95 ${
              selectedCategory === cat
                ? 'bg-[#134e40] text-white shadow-sm'
                : 'bg-white/80 hover:bg-white text-[#37474F] border border-[#cbd5e1]'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>}

      {/* 3. Opportunities List */}
      {!loading && !error && <div className="grid grid-cols-1 gap-5">
        {filtered.length === 0 && (
          <div className="bg-white/95 rounded-2xl p-6 border border-[#b8ded6] text-sm text-[#718078]">
            No verified opportunities match this sector.
          </div>
        )}
        {filtered.map((opp) => (
          <div
            key={opp.id}
            className="bg-white/95 rounded-2xl p-5 sm:p-6 border border-[#b8ded6] hover:border-[#134e40]/60 shadow-sm hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-5 group"
          >
            {/* Left Content */}
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                {/* Match Score Badge */}
                {typeof opp.matchScore === 'number' && <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300 flex items-center gap-1">
                  ★ {opp.matchScore}% Match
                </span>}
                <span className="text-xs font-medium text-[#718078] bg-[#FAF7F0] px-2.5 py-0.5 rounded-full border border-[#cbd5e1]">
                  {opp.category}
                </span>
                {opp.partner && <span className="text-xs text-[#134e40] font-medium">{opp.partner}</span>}
              </div>

              <h2 className="text-xl sm:text-2xl font-bold text-[#134e40] group-hover:text-[#0d3b30] transition-colors mb-2">
                {opp.title}
              </h2>

              {opp.overview && <p className="text-sm text-[#37474F] mb-3 leading-relaxed">{opp.overview}</p>}

              {/* Why it matches highlight box */}
              {opp.whyMatches && <div className="p-3 rounded-xl bg-[#FAF7F0] border border-[#b8ded6]/70 text-xs text-[#134e40] font-medium flex items-start gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-[#e69943] shrink-0 mt-0.5" />
                <span><strong className="text-[#134e40]">{getUIText('opportunities', 'whyMatches', langId)}</strong> {opp.whyMatches}</span>
              </div>}

              {/* Metadata tags */}
              <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-[#718078]">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-[#134e40]" />
                  {opp.location}
                </span>
                {opp.duration && <span className="font-semibold text-[#134e40]">{opp.duration}</span>}
                {opp.stipend && <span className="text-emerald-700 font-semibold">{opp.stipend}</span>}
              </div>
            </div>

            {/* Right Action */}
            <div className="flex md:flex-col items-center justify-between md:justify-center gap-3 pt-3 md:pt-0 border-t md:border-t-0 border-[#b8ded6]/50 shrink-0">
              <div className="text-left md:text-right">
                {opp.avgEarnings && <>
                  <span className="text-[11px] uppercase tracking-wider text-[#718078] block">Est. Earnings</span>
                  <span className="text-sm sm:text-base font-bold text-[#134e40]">{opp.avgEarnings}</span>
                </>}
              </div>

              <button
                onClick={() => onSelectOpportunity(opp)}
                className="px-5 py-2.5 rounded-full bg-[#134e40] hover:bg-[#0d3b30] text-white text-sm font-semibold flex items-center gap-1.5 shadow-sm active:scale-95 transition-all group-hover:shadow"
              >
                <span>{getUIText('opportunities', 'viewDetails', langId)}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>}
    </div>
  );
}
