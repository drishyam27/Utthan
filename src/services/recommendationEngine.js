/**
 * Utthan Deterministic Eligibility & Opportunity Matching Engine
 * 
 * Core Design Principles:
 * 1. Zero LLM hallucination for legal/administrative eligibility.
 * 2. Deterministic, verifiable rules (Location, Education, Age, Mobility).
 * 3. Transparent scoring matrix with explicit matched & unmet criteria reasons.
 */

const EDUCATION_LEVEL_RANKS = {
  'no_formal': 1,
  '8th_pass': 2,
  '10th_pass': 3,
  '12th_pass': 4,
  'iti_vocational': 5,
  'graduate': 6
};

const MOBILITY_LEVEL_RANKS = {
  'village_block': 1,
  'within_15km': 2,
  'district_wide': 3,
  'relocate_hostel': 4
};

// Normalizer to map human or survey answers to standard keys
export function normalizeEducation(input = '') {
  const str = String(input).toLowerCase();
  if (str.includes('graduat') || str.includes('degree')) return 'graduate';
  if (str.includes('iti') || str.includes('diploma') || str.includes('vocational')) return 'iti_vocational';
  if (str.includes('12') || str.includes('higher') || str.includes('উচ্চমাধ্যমিক')) return '12th_pass';
  if (str.includes('10') || str.includes('matric') || str.includes('secondary') || str.includes('মাধ্যমিক')) return '10th_pass';
  if (str.includes('8') || str.includes('middle') || str.includes('৮ম')) return '8th_pass';
  return 'no_formal';
}

export function normalizeMobility(input = '') {
  const str = String(input).toLowerCase();
  if (str.includes('relocate') || str.includes('hostel') || str.includes('হোস্টেল') || str.includes('बाहर')) return 'relocate_hostel';
  if (str.includes('district') || str.includes('জেলা') || str.includes('जिले')) return 'district_wide';
  if (str.includes('15') || str.includes('km') || str.includes('town') || str.includes('কসবা') || str.includes('শহর')) return 'within_15km';
  return 'village_block';
}

export function normalizeGoal(input = '') {
  const str = String(input).toLowerCase();
  if (str.includes('shop') || str.includes('business') || str.includes('দোকান') || str.includes('व्यवसाय') || str.includes('স্বনির্ভর')) return 'micro_business';
  if (str.includes('job') || str.includes('placement') || str.includes('পাক্কা চাকরি') || str.includes('पक्की नौकरी') || str.includes('কর্মসংস্থান')) return 'job_placement';
  return 'training_stipend'; // Default: certified training + stipend
}

/**
 * Check hard deterministic eligibility for an opportunity against beneficiary profile
 */
export function checkHardEligibility(beneficiary = {}, opportunity = {}) {
  const rules = opportunity.eligibilityRules || {};
  const unmetCriteria = [];
  const matchedCriteria = [];

  // 1. Geographic Check (State & District)
  const isPanIndia = rules.panIndia !== false && !opportunity.stateId;
  if (!isPanIndia) {
    const missingCanonicalLocation = !beneficiary.stateId
      || (opportunity.districtId && !beneficiary.districtId);

    if (missingCanonicalLocation) {
      unmetCriteria.push('Canonical State and District location is required for this restricted opportunity');
    } else if (opportunity.stateId && beneficiary.stateId !== opportunity.stateId) {
      unmetCriteria.push(`Location restricted to state: ${opportunity.stateId}`);
    } else if (opportunity.districtId && beneficiary.districtId !== opportunity.districtId) {
      unmetCriteria.push(`Location restricted to district: ${opportunity.districtId}`);
    } else {
      matchedCriteria.push('Geographic location matches program jurisdiction');
    }
  } else {
    matchedCriteria.push('Pan-India eligibility applies across all States and Districts');
  }

  // 2. Minimum Education Check
  const minEdu = opportunity.educationMin || rules.minEducation || 'no_formal';
  const minEduRank = EDUCATION_LEVEL_RANKS[minEdu] || 1;
  const userEduKey = normalizeEducation(beneficiary.education);
  const userEduRank = EDUCATION_LEVEL_RANKS[userEduKey] || 1;

  if (userEduRank < minEduRank) {
    unmetCriteria.push(`Minimum education required is ${minEdu.replace('_', ' ')} (beneficiary has ${userEduKey.replace('_', ' ')})`);
  } else {
    matchedCriteria.push(`Meets education qualification threshold (${userEduKey.replace('_', ' ')})`);
  }

  // 3. Age Limits Check (if beneficiary age is provided)
  const userAge = Number(beneficiary.age);
  if (!isNaN(userAge) && userAge > 0) {
    if (rules.minAge && userAge < rules.minAge) {
      unmetCriteria.push(`Minimum age required is ${rules.minAge} (beneficiary is ${userAge})`);
    } else if (rules.maxAge && userAge > rules.maxAge) {
      unmetCriteria.push(`Maximum age allowed is ${rules.maxAge} (beneficiary is ${userAge})`);
    } else {
      matchedCriteria.push(`Age (${userAge} years) within permissible bounds`);
    }
  }

  // 4. Mobility Requirement Check
  const requiredMobility = opportunity.mobilityRequirement || 'within_15km';
  const reqMobilityRank = MOBILITY_LEVEL_RANKS[requiredMobility] || 2;
  const userMobilityKey = normalizeMobility(beneficiary.mobility);
  const userMobilityRank = MOBILITY_LEVEL_RANKS[userMobilityKey] || 1;

  // If the program requires travel further than user can manage
  if (userMobilityRank < reqMobilityRank && (!rules.acceptedMobility || !rules.acceptedMobility.includes(userMobilityKey))) {
    unmetCriteria.push(`Opportunity requires travel: ${requiredMobility.replace('_', ' ')} (beneficiary prefers: ${userMobilityKey.replace('_', ' ')})`);
  } else {
    matchedCriteria.push(`Mobility preference matches commute requirements (${userMobilityKey.replace('_', ' ')})`);
  }

  const eligible = unmetCriteria.length === 0;
  return {
    eligible,
    matchedCriteria,
    unmetCriteria
  };
}

/**
 * Calculate deterministic match score for eligible opportunities
 * Weights:
 * - Trade / Skills Alignment: 40%
 * - Mobility Fit: 25%
 * - Education Fit: 20%
 * - Goal / Priority Fit: 15%
 * Total: 100%
 */
export function calculateMatchScore(beneficiary = {}, opportunity = {}) {
  let score = 0;
  const reasons = [];

  // A. Trade Alignment (40 pts)
  const targetKeywords = opportunity.targetTradeKeywords || [];
  const userTrade = String(beneficiary.trade || beneficiary.workInterest || '').toLowerCase();
  
  let keywordMatch = false;
  for (const kw of targetKeywords) {
    if (userTrade.includes(kw)) {
      keywordMatch = true;
      break;
    }
  }

  if (keywordMatch) {
    score += 40;
    reasons.push(`Direct alignment with your selected craft/trade interest (${userTrade})`);
  } else {
    // Check if category matches general trade cluster
    const cat = String(opportunity.category || '').toLowerCase();
    if (cat.includes(userTrade) || userTrade.includes(cat.split('/')[0].trim().toLowerCase())) {
      score += 25;
      reasons.push(`Related to your broader industry focus (${opportunity.category})`);
    } else {
      score += 15; // Baseline transferrable skill credit
      reasons.push(`Accessible foundation track for cross-skilling into ${opportunity.category}`);
    }
  }

  // B. Mobility Fit (25 pts)
  const userMobility = normalizeMobility(beneficiary.mobility);
  const oppMobility = opportunity.mobilityRequirement || 'within_15km';
  if (userMobility === oppMobility) {
    score += 25;
    reasons.push(`Convenient distance matching your exact travel preference (${userMobility.replace('_', ' ')})`);
  } else {
    score += 18;
    reasons.push(`Commute falls within feasible regional distance`);
  }

  // C. Education Fit (20 pts)
  const userEdu = normalizeEducation(beneficiary.education);
  const minEdu = opportunity.educationMin || 'no_formal';
  if (userEdu === minEdu) {
    score += 20;
    reasons.push(`Optimal qualification match for curriculum pace`);
  } else {
    score += 17;
    reasons.push(`Exceeds base qualification requirement, enabling faster completion`);
  }

  // D. Goal Fit (15 pts)
  const userGoal = normalizeGoal(beneficiary.goal || beneficiary.preference);
  const oppGoal = opportunity.primaryGoalFit || 'training_stipend';
  if (userGoal === oppGoal) {
    score += 15;
    reasons.push(`Directly fulfills your milestone goal (${userGoal.replace('_', ' ')})`);
  } else {
    score += 10;
    reasons.push(`Includes complementary pathways toward your future aspirations`);
  }

  return {
    score: Math.min(100, Math.max(0, score)),
    reasons
  };
}

/**
 * Main matching engine function:
 * Filters opportunities deterministically, scores eligible items, and returns ranked recommendations.
 */
export function matchOpportunities(beneficiary = {}, opportunitiesList = []) {
  const results = opportunitiesList.map((opportunity) => {
    const { eligible, matchedCriteria, unmetCriteria } = checkHardEligibility(beneficiary, opportunity);
    
    if (!eligible) {
      return {
        opportunity,
        eligible: false,
        score: 0,
        matchedCriteria,
        unmetCriteria,
        reasons: unmetCriteria
      };
    }

    const { score, reasons } = calculateMatchScore(beneficiary, opportunity);
    return {
      opportunity,
      eligible: true,
      score,
      matchedCriteria,
      unmetCriteria: [],
      reasons: [...reasons, ...matchedCriteria]
    };
  });

  // Sort: Eligible first by descending score, then by NSQF level descending; Ineligible last
  return results.sort((a, b) => {
    if (a.eligible && !b.eligible) return -1;
    if (!a.eligible && b.eligible) return 1;
    if (a.eligible && b.eligible) {
      if (b.score !== a.score) return b.score - a.score;
      return (b.opportunity.nsqfLevel || 0) - (a.opportunity.nsqfLevel || 0);
    }
    return 0;
  });
}
