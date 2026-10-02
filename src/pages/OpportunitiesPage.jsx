import React, { useEffect, useState } from 'react';
import { 
  Sparkles, MapPin, ArrowRight, Filter, AlertCircle, 
  CheckCircle2, Compass, ChevronDown, ChevronUp, XCircle 
} from 'lucide-react';
import { fetchOpportunities, fetchRecommendations, ApiError } from '../services/api';
import { mapOpportunity } from '../services/opportunityAdapter';
import { getUIText } from '../data/uiTranslations';

export default function OpportunitiesPage({ 
  currentLanguage,
  stateId,
  beneficiarySession,
  onSelectOpportunity,
  onStartInterview,
  onInvalidSession,
}) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [opportunities, setOpportunities] = useState([]);
  const [ineligibleOpportunities, setIneligibleOpportunities] = useState([]);
  const [recommendationStatus, setRecommendationStatus] = useState('none'); // 'none' | 'incomplete' | 'ready' | 'empty'
  const [showIneligible, setShowIneligible] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retryToken, setRetryToken] = useState(0);
  const langId = currentLanguage?.id || 'en';

  const categories = ['All', 'Green Energy', 'Traditional Craft', 'Agri-Tech', 'Healthcare', 'Dairy'];

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');

    const hasSession = Boolean(beneficiarySession?.beneficiaryId && beneficiarySession?.sessionToken);

    const catalogPromise = fetchOpportunities({ stateId }).catch(() => ({ opportunities: [] }));
    const recsPromise = hasSession
      ? fetchRecommendations(beneficiarySession.beneficiaryId, beneficiarySession.sessionToken)
      : Promise.resolve(null);

    Promise.all([catalogPromise, recsPromise])
      .then(([catalogPayload, recsPayload]) => {
        if (cancelled) return;

        const catalogList = (catalogPayload?.opportunities || []).map(opp => mapOpportunity(opp));
        const catalogMap = new Map(catalogList.map(opp => [opp.id, opp]));

        if (recsPayload) {
          if (recsPayload.has_completed_interview === false) {
            setRecommendationStatus('incomplete');
            setOpportunities(catalogList);
            setIneligibleOpportunities([]);
          } else {
            const recs = recsPayload.recommendations || [];
            const inelig = recsPayload.ineligible_opportunities || [];

            if (recs.length > 0) {
              setRecommendationStatus('ready');
              const mappedRecs = recs.map((r) => {
                const catItem = catalogMap.get(r.opportunity_id) || {};
                return mapOpportunity(
                  {
                    ...catItem,
                    id: r.opportunity_id,
                    title: r.title || catItem.title,
                    state_id: r.state_id ?? catItem.state_id,
                    district_id: r.district_id ?? catItem.district_id,
                    nsqf_level: r.nsqf_level ?? catItem.nsqf_level,
                    qp_code: r.qp_code ?? catItem.qp_code,
                  },
                  {
                    matchScore: r.score,
                    matchedCriteria: r.matched_criteria || [],
                    unmetCriteria: r.unmet_criteria || [],
                    reasons: r.reasons || [],
                    whyMatches: r.reasons?.[0] || null,
                    eligible: true,
                  }
                );
              });
              setOpportunities(mappedRecs);
            } else {
              setRecommendationStatus('empty');
              setOpportunities(catalogList);
            }

            const mappedInelig = inelig.map((inItem) => {
              const catItem = catalogMap.get(inItem.opportunity_id) || {};
              return mapOpportunity(
                {
                  ...catItem,
                  id: inItem.opportunity_id,
                  title: inItem.title || catItem.title,
                  state_id: inItem.state_id ?? catItem.state_id,
                  district_id: inItem.district_id ?? catItem.district_id,
                  nsqf_level: inItem.nsqf_level ?? catItem.nsqf_level,
                  qp_code: inItem.qp_code ?? catItem.qp_code,
                },
                {
                  matchScore: 0,
                  matchedCriteria: inItem.matched_criteria || [],
                  unmetCriteria: inItem.unmet_criteria || [],
                  reasons: inItem.reasons || inItem.unmet_criteria || [],
                  whyMatches: inItem.unmet_criteria?.[0] || null,
                  eligible: false,
                }
              );
            });
            setIneligibleOpportunities(mappedInelig);
          }
        } else {
          setRecommendationStatus('none');
          setOpportunities(catalogList);
          setIneligibleOpportunities([]);
        }
      })
      .catch((requestError) => {
        if (cancelled) return;
        if (requestError?.status === 401 || requestError?.status === 403) {
          if (onInvalidSession) onInvalidSession();
        }
        setError(requestError instanceof ApiError ? requestError.message : 'Opportunities could not be loaded.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [beneficiarySession?.beneficiaryId, beneficiarySession?.sessionToken, stateId, retryToken]);

  const filtered = selectedCategory === 'All'
    ? opportunities
    : opportunities.filter(o => (o.category || '').toLowerCase().includes(selectedCategory.toLowerCase()));

  const filteredIneligible = selectedCategory === 'All'
    ? ineligibleOpportunities
    : ineligibleOpportunities.filter(o => (o.category || '').toLowerCase().includes(selectedCategory.toLowerCase()));

  return (
    <div className="relative z-20 flex-1 px-4 sm:px-6 lg:px-12 py-8 max-w-5xl mx-auto w-full">
      {/* 1. Header Banner */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-3 py-1 rounded-full bg-[#134e40]/10 text-[#134e40] text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#e69943]" />
            {recommendationStatus === 'ready' 
              ? 'Deterministic Profile Matches' 
              : getUIText('opportunities', 'aiVerified', langId)}
          </span>
          <span className="text-xs text-[#718078]">
            {getUIText('opportunities', 'updatedRegion', langId)}
          </span>
        </div>
        <h1 className="font-serif-heading text-3xl sm:text-4xl lg:text-5xl font-bold text-[#134e40] mb-2">
          {recommendationStatus === 'ready' 
            ? 'Personalized Recommendations'
            : getUIText('opportunities', 'pageTitle', langId)}
        </h1>
        <p className="text-sm sm:text-base text-[#37474F] max-w-2xl">
          {recommendationStatus === 'ready'
            ? 'Government schemes and verified skilling tracks matched deterministically to your interview assessment, trade skills, and location commute.'
            : getUIText('opportunities', 'pageSubtitle', langId)}
        </p>
      </div>

      {/* 2. Status Callouts */}
      {!loading && !error && recommendationStatus === 'incomplete' && (
        <div className="mb-8 p-5 sm:p-6 rounded-2xl bg-[#FFF8EE] border border-[#FAD7AB] shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <Compass className="w-6 h-6 text-[#e69943] shrink-0 mt-0.5" />
            <div>
              <h2 className="text-base font-bold text-[#9e4c16] mb-1">
                Livelihood Assessment Incomplete
              </h2>
              <p className="text-xs sm:text-sm text-[#7a3b0e] leading-relaxed max-w-xl">
                Complete your brief 4-step conversational interview to receive personalized, NSQF-aligned scheme recommendations tailored to your exact skills, education, and district.
              </p>
            </div>
          </div>
          {onStartInterview && (
            <button
              onClick={onStartInterview}
              className="px-5 py-2.5 rounded-full bg-[#134e40] hover:bg-[#0d3b30] text-white text-xs sm:text-sm font-semibold flex items-center justify-center gap-1.5 shadow-sm active:scale-95 transition-all shrink-0"
            >
              <span>Complete Interview</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {!loading && !error && recommendationStatus === 'empty' && (
        <div className="mb-8 p-5 sm:p-6 rounded-2xl bg-white/95 border border-[#b8ded6] shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-[#718078] shrink-0 mt-0.5" />
            <div>
              <h2 className="text-base font-bold text-[#134e40] mb-1">
                No Exact Matches for Current Profile
              </h2>
              <p className="text-xs sm:text-sm text-[#37474F] leading-relaxed max-w-xl">
                None of the verified schemes currently match your exact combination of trade interest and travel preference. You can explore all state opportunities below or retake the interview to update your choices.
              </p>
            </div>
          </div>
          {onStartInterview && (
            <button
              onClick={onStartInterview}
              className="px-5 py-2.5 rounded-full bg-[#134e40] hover:bg-[#0d3b30] text-white text-xs sm:text-sm font-semibold flex items-center justify-center gap-1.5 shadow-sm active:scale-95 transition-all shrink-0"
            >
              <span>Retake Assessment</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {!loading && !error && recommendationStatus === 'none' && onStartInterview && (
        <div className="mb-8 p-4 sm:p-5 rounded-2xl bg-white/95 border border-[#b8ded6] shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs sm:text-sm">
          <div className="flex items-center gap-2.5 text-[#37474F]">
            <Sparkles className="w-4 h-4 text-[#e69943] shrink-0" />
            <span>Want personalized government recommendations? Complete a quick 2-minute voice interview.</span>
          </div>
          <button
            onClick={onStartInterview}
            className="font-bold text-[#134e40] hover:underline flex items-center gap-1 shrink-0"
          >
            <span>Start Voice Interview</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* 3. Loading & Error States */}
      {loading && (
        <div className="bg-white/95 rounded-2xl p-8 border border-[#b8ded6] text-center text-sm text-[#718078] shadow-sm">
          <Sparkles className="w-6 h-6 text-[#134e40] animate-pulse mx-auto mb-2" />
          Loading verified opportunities and recommendations...
        </div>
      )}

      {!loading && error && (
        <div className="bg-white/95 rounded-2xl p-6 border border-[#FAD7AB] text-sm text-[#7a3b0e] flex items-center justify-between gap-4 mb-6 shadow-sm">
          <span>{error}</span>
          <button onClick={() => setRetryToken((token) => token + 1)} className="font-bold text-[#134e40] hover:underline whitespace-nowrap">
            Retry loading
          </button>
        </div>
      )}

      {/* 4. Category Filter Pills */}
      {!loading && !error && (
        <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-6 scrollbar-none">
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
        </div>
      )}

      {/* 5. Primary Opportunities / Recommendations Grid */}
      {!loading && !error && (
        <div className="grid grid-cols-1 gap-5 mb-8">
          {filtered.length === 0 && (
            <div className="bg-white/95 rounded-2xl p-6 border border-[#b8ded6] text-sm text-[#718078]">
              No verified opportunities match this sector filter.
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
                  {typeof opp.matchScore === 'number' && opp.matchScore > 0 && (
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300 flex items-center gap-1">
                      ★ {opp.matchScore}% Profile Match
                    </span>
                  )}
                  <span className="text-xs font-medium text-[#718078] bg-[#FAF7F0] px-2.5 py-0.5 rounded-full border border-[#cbd5e1]">
                    {opp.category}
                  </span>
                  {opp.partner && <span className="text-xs text-[#134e40] font-medium">{opp.partner}</span>}
                  {opp.nsqf_level && (
                    <span className="text-xs font-semibold text-[#134e40] bg-[#134e40]/10 px-2 py-0.5 rounded-md">
                      NSQF Level {opp.nsqf_level}
                    </span>
                  )}
                </div>

                <h2 className="text-xl sm:text-2xl font-bold text-[#134e40] group-hover:text-[#0d3b30] transition-colors mb-2">
                  {opp.title}
                </h2>

                {opp.overview && <p className="text-sm text-[#37474F] mb-3 leading-relaxed">{opp.overview}</p>}

                {/* Why it matches highlight box */}
                {opp.whyMatches && (
                  <div className="p-3.5 rounded-xl bg-[#FAF7F0] border border-[#b8ded6]/70 text-xs text-[#134e40] mb-3">
                    <div className="flex items-start gap-2 mb-1.5">
                      <Sparkles className="w-4 h-4 text-[#e69943] shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-[#134e40]">Why this is recommended:</strong> {opp.whyMatches}
                      </span>
                    </div>

                    {opp.matchedCriteria && opp.matchedCriteria.length > 1 && (
                      <div className="flex flex-wrap gap-1.5 pl-6 pt-1">
                        {opp.matchedCriteria.slice(1).map((crit, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 text-[11px] bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded-md border border-emerald-200"
                          >
                            <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                            {crit}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

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
                  {opp.avgEarnings && (
                    <>
                      <span className="text-[11px] uppercase tracking-wider text-[#718078] block">Est. Earnings</span>
                      <span className="text-sm sm:text-base font-bold text-[#134e40]">{opp.avgEarnings}</span>
                    </>
                  )}
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
        </div>
      )}

      {/* 6. Ineligible Opportunities Section (Transparent Disclosure) */}
      {!loading && !error && filteredIneligible.length > 0 && (
        <div className="pt-4 border-t border-[#b8ded6]">
          <button
            onClick={() => setShowIneligible(prev => !prev)}
            className="flex items-center justify-between w-full p-4 rounded-2xl bg-white/80 hover:bg-white border border-[#cbd5e1] text-xs sm:text-sm font-semibold text-[#718078] transition-all"
          >
            <span className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-[#94a3b8]" />
              View Other Government Schemes Currently Ineligible ({filteredIneligible.length})
            </span>
            {showIneligible ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showIneligible && (
            <div className="grid grid-cols-1 gap-4 mt-4">
              {filteredIneligible.map((opp) => (
                <div
                  key={opp.id}
                  className="p-4 sm:p-5 rounded-2xl bg-white/60 border border-[#e2e8f0] opacity-80 hover:opacity-100 transition-opacity flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-gray-100 text-gray-700 border border-gray-300">
                        Statutory Criteria Unmet
                      </span>
                      <span className="text-xs text-[#718078]">{opp.category}</span>
                    </div>
                    <h3 className="text-base font-bold text-[#37474F] mb-1">
                      {opp.title}
                    </h3>
                    {opp.unmetCriteria && opp.unmetCriteria.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {opp.unmetCriteria.map((reason, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 text-[11px] bg-red-50 text-red-800 px-2 py-0.5 rounded border border-red-200"
                          >
                            <AlertCircle className="w-3 h-3 text-red-500 shrink-0" />
                            {reason}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => onSelectOpportunity(opp)}
                    className="px-4 py-2 rounded-full border border-[#cbd5e1] hover:border-[#134e40] text-xs font-semibold text-[#134e40] whitespace-nowrap self-start md:self-center"
                  >
                    View Criteria
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
