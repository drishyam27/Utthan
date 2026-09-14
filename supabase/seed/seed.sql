-- Utthan PostgreSQL Database Seed Script
-- Safe to re-run using ON CONFLICT DO NOTHING / UPDATE

-- ============================================================================
-- 1. SEED STATES (28 States + 8 UTs)
-- ============================================================================
INSERT INTO states (id, code, name, type) VALUES
('state-up', 'UP', 'Uttar Pradesh', 'state'),
('state-wb', 'WB', 'West Bengal', 'state'),
('state-br', 'BR', 'Bihar', 'state'),
('state-mh', 'MH', 'Maharashtra', 'state'),
('state-tn', 'TN', 'Tamil Nadu', 'state'),
('state-ap', 'AP', 'Andhra Pradesh', 'state'),
('state-tg', 'TG', 'Telangana', 'state'),
('state-ka', 'KA', 'Karnataka', 'state'),
('state-gj', 'GJ', 'Gujarat', 'state'),
('state-rj', 'RJ', 'Rajasthan', 'state'),
('state-mp', 'MP', 'Madhya Pradesh', 'state'),
('state-od', 'OD', 'Odisha', 'state'),
('state-kl', 'KL', 'Kerala', 'state'),
('state-jh', 'JH', 'Jharkhand', 'state'),
('state-as', 'AS', 'Assam', 'state'),
('state-pb', 'PB', 'Punjab', 'state'),
('state-hr', 'HR', 'Haryana', 'state'),
('state-ct', 'CT', 'Chhattisgarh', 'state'),
('state-ut', 'UT', 'Uttarakhand', 'state'),
('state-hp', 'HP', 'Himachal Pradesh', 'state'),
('state-tr', 'TR', 'Tripura', 'state'),
('state-ml', 'ML', 'Meghalaya', 'state'),
('state-mn', 'MN', 'Manipur', 'state'),
('state-nl', 'NL', 'Nagaland', 'state'),
('state-ga', 'GA', 'Goa', 'state'),
('state-ar', 'AR', 'Arunachal Pradesh', 'state'),
('state-mz', 'MZ', 'Mizoram', 'state'),
('state-sk', 'SK', 'Sikkim', 'state'),
('ut-dl', 'DL', 'Delhi (NCT)', 'union_territory'),
('ut-jk', 'JK', 'Jammu and Kashmir', 'union_territory'),
('ut-la', 'LA', 'Ladakh', 'union_territory'),
('ut-ch', 'CH', 'Chandigarh', 'union_territory'),
('ut-py', 'PY', 'Puducherry', 'union_territory'),
('ut-dn', 'DN', 'Dadra and Nagar Haveli and Daman and Diu', 'union_territory'),
('ut-an', 'AN', 'Andaman and Nicobar Islands', 'union_territory'),
('ut-ld', 'LD', 'Lakshadweep', 'union_territory')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, code = EXCLUDED.code;

-- ============================================================================
-- 2. SEED KEY DISTRICTS
-- ============================================================================
INSERT INTO districts (id, state_id, name, code) VALUES
-- Uttar Pradesh
('dist-up-varanasi', 'state-up', 'Varanasi', 'UP-VAR'),
('dist-up-lucknow', 'state-up', 'Lucknow', 'UP-LKO'),
('dist-up-prayagraj', 'state-up', 'Prayagraj', 'UP-PRY'),
('dist-up-gorakhpur', 'state-up', 'Gorakhpur', 'UP-GKP'),
('dist-up-kanpur', 'state-up', 'Kanpur Nagar', 'UP-KNP'),
('dist-up-ayodhya', 'state-up', 'Ayodhya', 'UP-AYO'),
-- West Bengal
('dist-wb-kolkata', 'state-wb', 'Kolkata', 'WB-KOL'),
('dist-wb-howrah', 'state-wb', 'Howrah', 'WB-HWH'),
('dist-wb-murshidabad', 'state-wb', 'Murshidabad', 'WB-MSD'),
('dist-wb-nadia', 'state-wb', 'Nadia', 'WB-NAD'),
('dist-wb-darjeeling', 'state-wb', 'Darjeeling', 'WB-DAR'),
-- Bihar
('dist-br-patna', 'state-br', 'Patna', 'BR-PAT'),
('dist-br-gaya', 'state-br', 'Gaya', 'BR-GAY'),
('dist-br-bhagalpur', 'state-br', 'Bhagalpur', 'BR-BGP'),
-- Maharashtra
('dist-mh-mumbai', 'state-mh', 'Mumbai City', 'MH-MUM'),
('dist-mh-pune', 'state-mh', 'Pune', 'MH-PUN'),
('dist-mh-nagpur', 'state-mh', 'Nagpur', 'MH-NGP'),
-- Tamil Nadu
('dist-tn-chennai', 'state-tn', 'Chennai', 'TN-CHE'),
('dist-tn-coimbatore', 'state-tn', 'Coimbatore', 'TN-CBE'),
-- Delhi
('dist-dl-central', 'ut-dl', 'Central Delhi', 'DL-CD'),
('dist-dl-south', 'ut-dl', 'South Delhi', 'DL-SD')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, code = EXCLUDED.code;

-- ============================================================================
-- 3. SEED SKILLS
-- ============================================================================
INSERT INTO skills (id, name, sector, nsqf_level, qp_code, source, source_url) VALUES
('skill-solar-inst', 'Solar PV Rooftop Installation', 'Green Jobs & Renewable Energy', 4, 'SGJ/Q0101', 'Skill Council for Green Jobs', 'https://sscgj.in'),
('skill-solar-wiring', 'DC Wiring & Inverter Safety', 'Green Jobs & Renewable Energy', 4, 'SGJ/Q0101', 'Skill Council for Green Jobs', 'https://sscgj.in'),
('skill-drone-nav', 'Agricultural Drone Navigation', 'Agriculture & Precision Farming', 4, 'AGR/Q7003', 'Agriculture Skill Council of India', 'https://asci-india.com'),
('skill-drone-spray', 'Micronutrient Spray & Crop Sensor Calibration', 'Agriculture & Precision Farming', 4, 'AGR/Q7003', 'Agriculture Skill Council of India', 'https://asci-india.com'),
('skill-tailoring-adv', 'Garment Construction & Pattern Cutting', 'Apparel & Handicrafts', 3, 'AMH/Q1947', 'Apparel Sector Skill Council', 'https://sscamh.com'),
('skill-loom-jacquard', 'Jacquard Loom Operation & Natural Dyeing', 'Textiles & Handloom', 4, 'TSC/Q7301', 'Textile Sector Skill Council', 'https://texskill.in'),
('skill-gda-vitals', 'Patient Vital Signs Monitoring & First Aid', 'Healthcare & Public Service', 4, 'HSS/Q5101', 'Healthcare Sector Skill Council', 'https://healthcare-ssc.in'),
('skill-gda-infection', 'Hospital Infection Control & Waste Handling', 'Healthcare & Public Service', 4, 'HSS/Q5101', 'Healthcare Sector Skill Council', 'https://healthcare-ssc.in'),
('skill-pashu-firstaid', 'Cattle First-Aid, Vaccination & Feed Silage', 'Animal Husbandry & Dairy', 3, 'AGR/Q4801', 'Agriculture Skill Council of India', 'https://asci-india.com'),
('skill-milk-fat-test', 'Electronic Milk Fat Analyzer Testing', 'Animal Husbandry & Dairy', 3, 'AGR/Q4801', 'National Dairy Development Board', 'https://www.nddb.coop'),
('skill-ev-battery', 'EV Battery Diagnostic & High-Voltage Safety', 'Automotive & Clean Mobility', 4, 'ASC/Q1411', 'Automotive Skills Development Council', 'https://asdc.org.in')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, qp_code = EXCLUDED.qp_code, nsqf_level = EXCLUDED.nsqf_level;

-- ============================================================================
-- 4. SEED VERIFIED OPPORTUNITIES
-- ============================================================================
INSERT INTO opportunities (
    id, title, category, provider, source, source_url, state_id, district_id,
    education_min, age_min, age_max, mobility_requirement, stipend, expected_earnings,
    duration, nsqf_level, qp_code, overview, primary_goal_fit, target_trade_keywords,
    eligibility_rules, application_url, active
) VALUES
(
    'opp-solar-rooftop',
    'Solar Micro-Grid & Rooftop Technician (Suryamitra)',
    'Green Energy / Technical',
    'PM Surya Ghar Muft Bijli Yojana / Skill Council for Green Jobs',
    'PM Surya Ghar Portal',
    'https://pmsuryaghar.gov.in',
    NULL, NULL,
    '10th_pass', 18, 40, 'within_15km',
    '₹4,500 / month practical stipend', '₹14,000 - ₹22,000 / month',
    '45 Days Practical Workshop (300 Hours)', 4, 'SGJ/Q0101',
    'Hands-on practical certification to install, wire, inspect, and maintain solar rooftop panels and rural mini-grids.',
    'training_stipend',
    ARRAY['solar', 'electrical', 'technician', 'electrician', 'energy', 'wireman'],
    '{"minAge": 18, "maxAge": 40, "minEducation": "10th_pass", "acceptedMobility": ["within_15km", "district_wide", "relocate_hostel"], "panIndia": true}'::jsonb,
    'https://skillindiadigital.gov.in/courses',
    TRUE
),
(
    'opp-pm-vishwakarma-tailor',
    'PM Vishwakarma Tailoring & Garment Enterprise Scheme',
    'Traditional Craft & Textiles',
    'Ministry of MSME & National Skill Development Corporation',
    'PM Vishwakarma Official Portal',
    'https://pmvishwakarma.gov.in',
    NULL, NULL,
    'no_formal', 18, NULL, 'village_block',
    '₹500 / day stipend during 5-day basic training + ₹15,000 Toolkit E-Voucher', '₹12,000 - ₹25,000 / month + MUDRA credit support',
    '5 to 7 Days Basic Training + Optional 15-Day Advanced', 3, 'AMH/Q1947',
    'Special scheme for traditional artisans and tailors. Includes ₹15,000 modern sewing tool voucher and 5% interest loan up to ₹3,00,000 without collateral.',
    'micro_business',
    ARRAY['tailoring', 'sewing', 'textile', 'weaving', 'garment', 'fashion', 'handloom'],
    '{"minAge": 18, "maxAge": null, "minEducation": "no_formal", "acceptedMobility": ["village_block", "within_15km", "district_wide", "relocate_hostel"], "panIndia": true}'::jsonb,
    'https://pmvishwakarma.gov.in/Registration',
    TRUE
),
(
    'opp-kisan-drone-pilot',
    'Agricultural Drone Pilot & Precision Farming Specialist',
    'Agri-Tech / Modern Farming',
    'Ministry of Agriculture / DGCA Certified Training Institute',
    'Kisan Drone Scheme & Skill India Digital',
    'https://agricoop.nic.in',
    NULL, NULL,
    '10th_pass', 18, 35, 'district_wide',
    'Subsidized under Namo Drone Didi / Agri-Infra Fund', '₹18,000 - ₹30,000 / month during crop cycles',
    '15 Days Intensive Flight Training', 4, 'AGR/Q7003',
    'Learn to pilot DGCA-approved drones for aerial spraying of nano-fertilizers and real-time crop disease detection.',
    'job_placement',
    ARRAY['drone', 'agriculture', 'farming', 'agri', 'pilot', 'sensor', 'spraying'],
    '{"minAge": 18, "maxAge": 35, "minEducation": "10th_pass", "acceptedMobility": ["district_wide", "relocate_hostel"], "panIndia": true}'::jsonb,
    'https://skillindiadigital.gov.in',
    TRUE
),
(
    'opp-ddu-gky-gda',
    'General Duty Healthcare Assistant (Aarogya Sathi)',
    'Healthcare & Public Service',
    'DDU-GKY / Healthcare Sector Skill Council',
    'Deen Dayal Upadhyaya Grameen Kaushalya Yojana',
    'https://ddugky.gov.in',
    NULL, NULL,
    '10th_pass', 18, 35, 'within_15km',
    '₹5,000 / month + Free Boarding & Uniform', '₹12,000 - ₹18,000 / month guaranteed placement',
    '90 Days Residential Training', 4, 'HSS/Q5101',
    'Full residential healthcare certification under Ministry of Rural Development with hospital internship.',
    'job_placement',
    ARRAY['health', 'healthcare', 'nurse', 'hospital', 'patient', 'medical', 'gda', 'clinic'],
    '{"minAge": 18, "maxAge": 35, "minEducation": "10th_pass", "acceptedMobility": ["within_15km", "district_wide", "relocate_hostel"], "panIndia": true}'::jsonb,
    'https://ddugky.gov.in/candidate-registration',
    TRUE
),
(
    'opp-nrlm-pashu-sakhi',
    'Rural Dairy & Pashu Sakhi Micro-Enterprise',
    'Animal Husbandry & Dairy',
    'National Rural Livelihoods Mission (Lakhpati Didi) / NDDB',
    'National Rural Livelihoods Mission (DAY-NRLM)',
    'https://aajeevika.gov.in',
    NULL, NULL,
    '8th_pass', 18, 50, 'village_block',
    'Free RSETI training + ₹3,000 post-training kit support', '₹15,000 - ₹35,000 / month',
    '21 Days Fast-track Hands-on Training', 3, 'AGR/Q4801',
    'Empowers rural women and youth to manage cattle vaccination schedules, silage nutrition, and automated milk fat testing.',
    'micro_business',
    ARRAY['dairy', 'animal', 'cattle', 'cow', 'milk', 'livestock', 'veterinary', 'farming'],
    '{"minAge": 18, "maxAge": 50, "minEducation": "8th_pass", "acceptedMobility": ["village_block", "within_15km", "district_wide", "relocate_hostel"], "panIndia": true}'::jsonb,
    'https://aajeevika.gov.in',
    TRUE
),
(
    'opp-pm-ajay-handloom-varanasi',
    'PM-AJAY GIA Modern Jacquard Handloom & ONDC Cluster',
    'Traditional Craft & Textiles',
    'Ministry of Social Justice & Empowerment / Development Commissioner (Handlooms)',
    'PM-AJAY GIA Component',
    'https://socialjustice.gov.in/schemes/37',
    'state-up', 'dist-up-varanasi',
    'no_formal', 18, NULL, 'village_block',
    'Raw material grant + ₹3,500 monthly stipend', '₹14,000 - ₹28,000 / month + Direct buyer linkage',
    '30 Days Master Artisan Upgrade', 4, 'TSC/Q7301',
    'Specialized PM-AJAY GIA initiative for SC artisan clusters in Varanasi district with upgraded Jacquard looms.',
    'micro_business',
    ARRAY['handloom', 'weaving', 'textile', 'jacquard', 'craft', 'artisan', 'silk'],
    '{"minAge": 18, "maxAge": null, "minEducation": "no_formal", "acceptedMobility": ["village_block", "within_15km", "district_wide", "relocate_hostel"], "panIndia": false, "stateId": "state-up", "districtId": "dist-up-varanasi"}'::jsonb,
    'https://handlooms.nic.in',
    TRUE
),
(
    'opp-pmkvy-ev-service',
    'Electric Vehicle (EV) Service & Battery Technician',
    'Automotive & Clean Mobility',
    'Automotive Skills Development Council (ASDC) / PMKVY 4.0',
    'Skill India Digital Hub',
    'https://skillindiadigital.gov.in',
    NULL, NULL,
    '10th_pass', 18, 35, 'within_15km',
    '₹4,000 / month allowance + Tool safety gear', '₹15,000 - ₹26,000 / month',
    '60 Days Certification Program', 4, 'ASC/Q1411',
    'Comprehensive high-voltage safety, battery cell balancing, and electrical drivetrain servicing for commercial EVs.',
    'job_placement',
    ARRAY['ev', 'electric', 'vehicle', 'automotive', 'battery', 'mechanic', 'automobile'],
    '{"minAge": 18, "maxAge": 35, "minEducation": "10th_pass", "acceptedMobility": ["within_15km", "district_wide", "relocate_hostel"], "panIndia": true}'::jsonb,
    'https://skillindiadigital.gov.in',
    TRUE
)
ON CONFLICT (id) DO UPDATE SET 
    title = EXCLUDED.title,
    stipend = EXCLUDED.stipend,
    expected_earnings = EXCLUDED.expected_earnings,
    eligibility_rules = EXCLUDED.eligibility_rules;

-- ============================================================================
-- 5. SEED OPPORTUNITY_SKILLS MAPPINGS
-- ============================================================================
INSERT INTO opportunity_skills (opportunity_id, skill_id, is_taught, priority) VALUES
('opp-solar-rooftop', 'skill-solar-inst', true, 1),
('opp-solar-rooftop', 'skill-solar-wiring', true, 2),
('opp-pm-vishwakarma-tailor', 'skill-tailoring-adv', true, 1),
('opp-kisan-drone-pilot', 'skill-drone-nav', true, 1),
('opp-kisan-drone-pilot', 'skill-drone-spray', true, 2),
('opp-ddu-gky-gda', 'skill-gda-vitals', true, 1),
('opp-ddu-gky-gda', 'skill-gda-infection', true, 2),
('opp-nrlm-pashu-sakhi', 'skill-pashu-firstaid', true, 1),
('opp-nrlm-pashu-sakhi', 'skill-milk-fat-test', true, 2),
('opp-pm-ajay-handloom-varanasi', 'skill-loom-jacquard', true, 1),
('opp-pmkvy-ev-service', 'skill-ev-battery', true, 1)
ON CONFLICT (opportunity_id, skill_id) DO NOTHING;
