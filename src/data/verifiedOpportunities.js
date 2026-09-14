/**
 * Utthan Verified Opportunities & Standardized Skills Dataset
 * Sources:
 * - PM Vishwakarma Portal (pmvishwakarma.gov.in)
 * - PM Surya Ghar: Muft Bijli Yojana (pmsuryaghar.gov.in)
 * - Skill India Digital Hub / PMKVY 4.0 (skillindiadigital.gov.in)
 * - Deen Dayal Upadhyaya Grameen Kaushalya Yojana (ddugky.gov.in)
 * - National Rural Livelihoods Mission / Lakhpati Didi (aajeevika.gov.in)
 * - Ministry of Social Justice & Empowerment - PM-AJAY GIA (socialjustice.gov.in)
 */

export const SKILLS_MASTER = [
  {
    id: 'skill-solar-inst',
    name: 'Solar PV Rooftop Installation',
    sector: 'Green Jobs & Renewable Energy',
    nsqfLevel: 4,
    qpCode: 'SGJ/Q0101',
    source: 'Skill Council for Green Jobs',
    sourceUrl: 'https://sscgj.in'
  },
  {
    id: 'skill-solar-wiring',
    name: 'DC Wiring & Inverter Safety',
    sector: 'Green Jobs & Renewable Energy',
    nsqfLevel: 4,
    qpCode: 'SGJ/Q0101',
    source: 'Skill Council for Green Jobs',
    sourceUrl: 'https://sscgj.in'
  },
  {
    id: 'skill-drone-nav',
    name: 'Agricultural Drone Navigation',
    sector: 'Agriculture & Precision Farming',
    nsqfLevel: 4,
    qpCode: 'AGR/Q7003',
    source: 'Agriculture Skill Council of India (ASCI)',
    sourceUrl: 'https://asci-india.com'
  },
  {
    id: 'skill-drone-spray',
    name: 'Micronutrient Spray & Crop Sensor Calibration',
    sector: 'Agriculture & Precision Farming',
    nsqfLevel: 4,
    qpCode: 'AGR/Q7003',
    source: 'Agriculture Skill Council of India (ASCI)',
    sourceUrl: 'https://asci-india.com'
  },
  {
    id: 'skill-tailoring-adv',
    name: 'Garment Construction & Pattern Cutting',
    sector: 'Apparel & Handicrafts',
    nsqfLevel: 3,
    qpCode: 'AMH/Q1947',
    source: 'Apparel Made-Ups and Home Furnishing SSC',
    sourceUrl: 'https://sscamh.com'
  },
  {
    id: 'skill-loom-jacquard',
    name: 'Jacquard Loom Operation & Natural Dyeing',
    sector: 'Textiles & Handloom',
    nsqfLevel: 4,
    qpCode: 'TSC/Q7301',
    source: 'Textile Sector Skill Council (TSC)',
    sourceUrl: 'https://texskill.in'
  },
  {
    id: 'skill-gda-vitals',
    name: 'Patient Vital Signs Monitoring & First Aid',
    sector: 'Healthcare & Public Service',
    nsqfLevel: 4,
    qpCode: 'HSS/Q5101',
    source: 'Healthcare Sector Skill Council (HSSC)',
    sourceUrl: 'https://healthcare-ssc.in'
  },
  {
    id: 'skill-gda-infection',
    name: 'Hospital Infection Control & Waste Handling',
    sector: 'Healthcare & Public Service',
    nsqfLevel: 4,
    qpCode: 'HSS/Q5101',
    source: 'Healthcare Sector Skill Council (HSSC)',
    sourceUrl: 'https://healthcare-ssc.in'
  },
  {
    id: 'skill-pashu-firstaid',
    name: 'Cattle First-Aid, Vaccination & Feed Silage',
    sector: 'Animal Husbandry & Dairy',
    nsqfLevel: 3,
    qpCode: 'AGR/Q4801',
    source: 'Agriculture Skill Council of India (ASCI)',
    sourceUrl: 'https://asci-india.com'
  },
  {
    id: 'skill-milk-fat-test',
    name: 'Electronic Milk Fat Analyzer Testing',
    sector: 'Animal Husbandry & Dairy',
    nsqfLevel: 3,
    qpCode: 'AGR/Q4801',
    source: 'National Dairy Development Board (NDDB)',
    sourceUrl: 'https://www.nddb.coop'
  },
  {
    id: 'skill-ev-battery',
    name: 'EV Battery Diagnostic & High-Voltage Safety',
    sector: 'Automotive & Clean Mobility',
    nsqfLevel: 4,
    qpCode: 'ASC/Q1411',
    source: 'Automotive Skills Development Council (ASDC)',
    sourceUrl: 'https://asdc.org.in'
  }
];

export const VERIFIED_OPPORTUNITIES = [
  {
    id: 'opp-solar-rooftop',
    title: 'Solar Micro-Grid & Rooftop Technician (Suryamitra)',
    category: 'Green Energy / Technical',
    provider: 'PM Surya Ghar Muft Bijli Yojana / Skill Council for Green Jobs',
    source: 'PM Surya Ghar Portal',
    sourceUrl: 'https://pmsuryaghar.gov.in',
    stateId: null, // Pan-India
    districtId: null,
    targetTradeKeywords: ['solar', 'electrical', 'technician', 'electrician', 'energy', 'wireman'],
    educationMin: '10th_pass', // 'no_formal', '8th_pass', '10th_pass', '12th_pass', 'iti_vocational', 'graduate'
    ageMin: 18,
    ageMax: 40,
    mobilityRequirement: 'within_15km', // 'village_block', 'within_15km', 'district_wide', 'relocate_hostel'
    stipend: '₹4,500 / month practical stipend',
    expectedEarnings: '₹14,000 - ₹22,000 / month',
    duration: '45 Days Practical Workshop (300 Hours)',
    nsqfLevel: 4,
    qpCode: 'SGJ/Q0101',
    applicationUrl: 'https://skillindiadigital.gov.in/courses',
    active: true,
    overview: 'Hands-on practical certification to install, wire, inspect, and maintain solar rooftop panels and rural mini-grids under PM Surya Ghar and PM-KUSUM.',
    eligibilityRules: {
      minAge: 18,
      maxAge: 40,
      minEducation: '10th_pass',
      acceptedMobility: ['within_15km', 'district_wide', 'relocate_hostel'],
      panIndia: true
    },
    primaryGoalFit: 'training_stipend', // 'training_stipend', 'job_placement', 'micro_business'
    skillIds: ['skill-solar-inst', 'skill-solar-wiring'],
    actionSteps: [
      { step: 1, title: 'Verify Aadhaar & Register on Skill India', desc: 'Assisted registration via Utthan', status: 'completed' },
      { step: 2, title: 'Attend Orientation at Local ITI', desc: 'Receive safety toolkit and electrical handbook', status: 'current' },
      { step: 3, title: '45-Day Practical Training', desc: 'Rooftop wiring on 10 community test sites', status: 'upcoming' },
      { step: 4, title: 'NSDC Skill Certification Exam', desc: 'Theory and hands-on demonstration', status: 'upcoming' },
      { step: 5, title: 'Empanelment with Solar Discom Contractor', desc: 'Onboarding for local installations', status: 'upcoming' }
    ]
  },
  {
    id: 'opp-pm-vishwakarma-tailor',
    title: 'PM Vishwakarma Tailoring & Garment Enterprise Scheme',
    category: 'Traditional Craft & Textiles',
    provider: 'Ministry of MSME & National Skill Development Corporation',
    source: 'PM Vishwakarma Official Portal',
    sourceUrl: 'https://pmvishwakarma.gov.in',
    stateId: null, // Pan-India
    districtId: null,
    targetTradeKeywords: ['tailoring', 'sewing', 'textile', 'weaving', 'garment', 'fashion', 'handloom'],
    educationMin: 'no_formal',
    ageMin: 18,
    ageMax: null, // No upper age limit
    mobilityRequirement: 'village_block',
    stipend: '₹500 / day stipend during 5-day basic training + ₹15,000 Toolkit E-Voucher',
    expectedEarnings: '₹12,000 - ₹25,000 / month + MUDRA credit support',
    duration: '5 to 7 Days Basic Training + Optional 15-Day Advanced',
    nsqfLevel: 3,
    qpCode: 'AMH/Q1947',
    applicationUrl: 'https://pmvishwakarma.gov.in/Registration',
    active: true,
    overview: 'Special scheme for traditional artisans and tailors. Includes ₹15,000 modern sewing tool voucher, certified training, and 5% interest enterprise loan up to ₹3,00,000 without collateral.',
    eligibilityRules: {
      minAge: 18,
      maxAge: null,
      minEducation: 'no_formal',
      acceptedMobility: ['village_block', 'within_15km', 'district_wide', 'relocate_hostel'],
      panIndia: true
    },
    primaryGoalFit: 'micro_business',
    skillIds: ['skill-tailoring-adv'],
    actionSteps: [
      { step: 1, title: 'Gram Panchayat / CSC Verification', desc: 'Bio-metric authentication of traditional trade', status: 'completed' },
      { step: 2, title: '5-Day Basic Skill Upgradation', desc: 'Modern pattern design and electric sewing machines', status: 'current' },
      { step: 3, title: '₹15,000 Toolkit Incentive Disbursal', desc: 'Direct digital voucher for purchasing machinery', status: 'upcoming' },
      { step: 4, title: 'PM Vishwakarma Certificate & ID Card', desc: 'Nationally recognized artisan card', status: 'upcoming' },
      { step: 5, title: 'Tranche-1 Collateral-Free Loan (₹1 Lakh)', desc: 'Concessional 5% interest rate', status: 'upcoming' }
    ]
  },
  {
    id: 'opp-kisan-drone-pilot',
    title: 'Agricultural Drone Pilot & Precision Farming Specialist',
    category: 'Agri-Tech / Modern Farming',
    provider: 'Ministry of Agriculture / DGCA Certified Training Institute',
    source: 'Kisan Drone Scheme & Skill India Digital',
    sourceUrl: 'https://agricoop.nic.in',
    stateId: null, // Pan-India
    districtId: null,
    targetTradeKeywords: ['drone', 'agriculture', 'farming', 'agri', 'pilot', 'sensor', 'spraying'],
    educationMin: '10th_pass',
    ageMin: 18,
    ageMax: 35,
    mobilityRequirement: 'district_wide',
    stipend: 'Subsidized under Namo Drone Didi / Agri-Infra Fund',
    expectedEarnings: '₹18,000 - ₹30,000 / month during crop cycles',
    duration: '15 Days Intensive Flight Training (Simulation + Field Flying)',
    nsqfLevel: 4,
    qpCode: 'AGR/Q7003',
    applicationUrl: 'https://skillindiadigital.gov.in',
    active: true,
    overview: 'Learn to pilot DGCA-approved drones for aerial spraying of nano-fertilizers and real-time crop disease detection. High rural contractor demand.',
    eligibilityRules: {
      minAge: 18,
      maxAge: 35,
      minEducation: '10th_pass',
      acceptedMobility: ['district_wide', 'relocate_hostel'],
      panIndia: true
    },
    primaryGoalFit: 'job_placement',
    skillIds: ['skill-drone-nav', 'skill-drone-spray'],
    actionSteps: [
      { step: 1, title: 'Class 2 Medical Fitness Clearance', desc: 'Conducted at district hospital', status: 'completed' },
      { step: 2, title: 'Simulator Ground Training (5 Days)', desc: 'Practice virtual takeoff, hovering, and safety return', status: 'upcoming' },
      { step: 3, title: 'Live Demonstration Spraying (10 Days)', desc: 'Field trials over agricultural acreage', status: 'upcoming' },
      { step: 4, title: 'DGCA Remote Pilot License (RPL) Award', desc: 'Government commercial pilot certificate', status: 'upcoming' },
      { step: 5, title: 'FPO Commercial Service Contract', desc: 'Assigned to cover 10-15 Gram Panchayats', status: 'upcoming' }
    ]
  },
  {
    id: 'opp-ddu-gky-gda',
    title: 'General Duty Healthcare Assistant (Aarogya Sathi)',
    category: 'Healthcare & Public Service',
    provider: 'DDU-GKY / Healthcare Sector Skill Council',
    source: 'Deen Dayal Upadhyaya Grameen Kaushalya Yojana',
    sourceUrl: 'https://ddugky.gov.in',
    stateId: null, // Pan-India
    districtId: null,
    targetTradeKeywords: ['health', 'healthcare', 'nurse', 'hospital', 'patient', 'medical', 'gda', 'clinic'],
    educationMin: '10th_pass',
    ageMin: 18,
    ageMax: 35,
    mobilityRequirement: 'within_15km',
    stipend: '₹5,000 / month + Free Boarding & Uniform',
    expectedEarnings: '₹12,000 - ₹18,000 / month guaranteed placement',
    duration: '90 Days Residential Training (Including Hospital Shadowing)',
    nsqfLevel: 4,
    qpCode: 'HSS/Q5101',
    applicationUrl: 'https://ddugky.gov.in/candidate-registration',
    active: true,
    overview: 'Full residential healthcare certification under Ministry of Rural Development. Guaranteed placement in private/trust hospitals and community health centers.',
    eligibilityRules: {
      minAge: 18,
      maxAge: 35,
      minEducation: '10th_pass',
      acceptedMobility: ['within_15km', 'district_wide', 'relocate_hostel'],
      panIndia: true
    },
    primaryGoalFit: 'job_placement',
    skillIds: ['skill-gda-vitals', 'skill-gda-infection'],
    actionSteps: [
      { step: 1, title: 'BPL / Rural Poor Verification', desc: 'Enrolled under DDU-GKY state portal', status: 'completed' },
      { step: 2, title: 'Foundational Clinical Training (6 Weeks)', desc: 'Anatomy, first aid, vitals & patient communication', status: 'current' },
      { step: 3, title: 'Hospital Internship & Shadowing', desc: '30 days rotation at empaneled district hospital', status: 'upcoming' },
      { step: 4, title: 'HSSC Skill Assessment & Certificate', desc: 'Certified General Duty Assistant', status: 'upcoming' },
      { step: 5, title: 'Direct Employment Onboarding', desc: 'Letter of appointment with healthcare partner', status: 'upcoming' }
    ]
  },
  {
    id: 'opp-nrlm-pashu-sakhi',
    title: 'Rural Dairy & Pashu Sakhi Micro-Enterprise',
    category: 'Animal Husbandry & Dairy',
    provider: 'National Rural Livelihoods Mission (Lakhpati Didi) / NDDB',
    source: 'National Rural Livelihoods Mission (DAY-NRLM)',
    sourceUrl: 'https://aajeevika.gov.in',
    stateId: null, // Pan-India
    districtId: null,
    targetTradeKeywords: ['dairy', 'animal', 'cattle', 'cow', 'milk', 'livestock', 'veterinary', 'farming'],
    educationMin: '8th_pass',
    ageMin: 18,
    ageMax: 50,
    mobilityRequirement: 'village_block',
    stipend: 'Free RSETI training + ₹3,000 post-training kit support',
    expectedEarnings: '₹15,000 - ₹35,000 / month',
    duration: '21 Days Fast-track Hands-on Training',
    nsqfLevel: 3,
    qpCode: 'AGR/Q4801',
    applicationUrl: 'https://aajeevika.gov.in',
    active: true,
    overview: 'Empowers rural women and youth to manage cattle vaccination schedules, silage nutrition, and automated milk fat testing for cooperative chilling centers.',
    eligibilityRules: {
      minAge: 18,
      maxAge: 50,
      minEducation: '8th_pass',
      acceptedMobility: ['village_block', 'within_15km', 'district_wide', 'relocate_hostel'],
      panIndia: true
    },
    primaryGoalFit: 'micro_business',
    skillIds: ['skill-pashu-firstaid', 'skill-milk-fat-test'],
    actionSteps: [
      { step: 1, title: 'SHG / Village Organization Endorsement', desc: 'Nomination by Gram Panchayat cluster', status: 'completed' },
      { step: 2, title: '21-Day RSETI Practical Training', desc: 'Veterinary first aid and milk testing equipment', status: 'upcoming' },
      { step: 3, title: 'Dairy Cooperative Collection Agreement', desc: 'Designation of daily milk collection point', status: 'upcoming' },
      { step: 4, title: 'MUDRA / SHG Collateral-Free Credit', desc: '₹50,000 equipment acquisition credit', status: 'upcoming' }
    ]
  },
  {
    id: 'opp-pm-ajay-handloom-varanasi',
    title: 'PM-AJAY GIA Modern Jacquard Handloom & ONDC Cluster',
    category: 'Traditional Craft & Textiles',
    provider: 'Ministry of Social Justice & Empowerment / Development Commissioner (Handlooms)',
    source: 'PM-AJAY GIA Component',
    sourceUrl: 'https://socialjustice.gov.in/schemes/37',
    stateId: 'state-up', // State specific (Uttar Pradesh)
    districtId: 'dist-up-varanasi', // District specific (Varanasi)
    targetTradeKeywords: ['handloom', 'weaving', 'textile', 'jacquard', 'craft', 'artisan', 'silk'],
    educationMin: 'no_formal',
    ageMin: 18,
    ageMax: null,
    mobilityRequirement: 'village_block',
    stipend: 'Raw material grant + ₹3,500 monthly stipend',
    expectedEarnings: '₹14,000 - ₹28,000 / month + Direct buyer linkage',
    duration: '30 Days Master Artisan Upgrade',
    nsqfLevel: 4,
    qpCode: 'TSC/Q7301',
    applicationUrl: 'https://handlooms.nic.in',
    active: true,
    overview: 'Specialized PM-AJAY GIA initiative for SC artisan clusters in Varanasi district. Upgrades traditional pit looms to ergonomic Jacquard looms with direct ONDC digital storefront onboarding.',
    eligibilityRules: {
      minAge: 18,
      maxAge: null,
      minEducation: 'no_formal',
      acceptedMobility: ['village_block', 'within_15km', 'district_wide', 'relocate_hostel'],
      panIndia: false,
      stateId: 'state-up',
      districtId: 'dist-up-varanasi'
    },
    primaryGoalFit: 'micro_business',
    skillIds: ['skill-loom-jacquard'],
    actionSteps: [
      { step: 1, title: 'PM-AJAY Beneficiary Cluster Enrollment', desc: 'Verification at District Welfare Office', status: 'completed' },
      { step: 2, title: '30-Day Jacquard Design Workshop', desc: 'Contemporary colorfast dyeing and motif punch cards', status: 'current' },
      { step: 3, title: 'Upgraded Loom Machinery Delivery', desc: 'Government subsidized Jacquard assembly', status: 'upcoming' },
      { step: 4, title: 'ONDC Crafts E-Commerce Onboarding', desc: 'Listing directly on national digital commerce grid', status: 'upcoming' }
    ]
  },
  {
    id: 'opp-pmkvy-ev-service',
    title: 'Electric Vehicle (EV) Service & Battery Technician',
    category: 'Automotive & Clean Mobility',
    provider: 'Automotive Skills Development Council (ASDC) / PMKVY 4.0',
    source: 'Skill India Digital Hub',
    sourceUrl: 'https://skillindiadigital.gov.in',
    stateId: null, // Pan-India
    districtId: null,
    targetTradeKeywords: ['ev', 'electric', 'vehicle', 'automotive', 'battery', 'mechanic', 'automobile'],
    educationMin: '10th_pass',
    ageMin: 18,
    ageMax: 35,
    mobilityRequirement: 'within_15km',
    stipend: '₹4,000 / month allowance + Tool safety gear',
    expectedEarnings: '₹15,000 - ₹26,000 / month',
    duration: '60 Days Certification Program',
    nsqfLevel: 4,
    qpCode: 'ASC/Q1411',
    applicationUrl: 'https://skillindiadigital.gov.in',
    active: true,
    overview: 'Comprehensive high-voltage safety, battery cell balancing, and electrical drivetrain servicing for 2-wheeler and 3-wheeler commercial EVs.',
    eligibilityRules: {
      minAge: 18,
      maxAge: 35,
      minEducation: '10th_pass',
      acceptedMobility: ['within_15km', 'district_wide', 'relocate_hostel'],
      panIndia: true
    },
    primaryGoalFit: 'job_placement',
    skillIds: ['skill-ev-battery'],
    actionSteps: [
      { step: 1, title: 'Skill India Digital Enrollment', desc: 'Verification of 10th marksheet & ID', status: 'completed' },
      { step: 2, title: 'Classroom & High-Voltage Lab Training', desc: 'Multimeter diagnostics, battery pack safety', status: 'upcoming' },
      { step: 3, title: 'OEM Workshop Apprenticeship', desc: '30 days hands-on at certified EV service dealership', status: 'upcoming' },
      { step: 4, title: 'ASDC Certified EV Technician Credential', desc: 'Official government skill credential', status: 'upcoming' }
    ]
  }
];
