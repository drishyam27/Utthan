# NSQF / NQR Course Dataset Audit Report

**Project**: Utthan — AI-Driven Voice Assistant for Livelihood Mapping & NSQF-Aligned Skilling Recommendations for SC Communities (PM-AJAY GIA)  
**Date**: October 3, 2026  
**Auditor**: Antigravity Autonomous Engineering Agent  
**Dataset Directory**: `NSQF-NQR Course Dataset/`  

---

## 1. Executive Summary

A comprehensive data audit was conducted on all workbook files in the `NSQF-NQR Course Dataset/` directory to establish the authoritative National Skills Qualifications Framework (NSQF) / National Qualification Register (NQR) course catalog for Utthan.

* **Total Files Inspected**: 44 Microsoft Excel (`.xlsx`) workbooks
* **Sheet Structure**: Uniform across all 44 files; single sheet named `Worksheet`
* **Layout**: Uniform across all 44 files; Row 1 banner, Row 2 column headers (18 columns), Row 3+ qualification records
* **Total Source Records**: **2,810** course qualifications
* **Total Distinct Sectors**: **44** sectors
* **Excluded Sectors Found**: **0** of the 15 excluded sectors are present in this dataset (100% of the 2,810 records are eligible for ingestion)
* **Missing Essential Fields**: 0 missing titles, 0 missing codes, 0 missing levels, 0 missing sectors
* **Duplicate Codes**: Exactly 1 duplicate qualification code (`QG-04-ES-00913-2023-V1-SCGJ` shared by two distinct valid courses in Green Jobs)
* **PwD Qualifications**: **231** courses dedicated to Persons with Disability, spanning Visual Impairment (VI), Speech & Hearing Impairment (SHI), Locomotor Disability (LD), and Intellectual Disability (ID)

---

## 2. Source Column Schema (18 Columns)

All 44 Excel workbooks share the exact same 18-column structure:

| Col # | Header Name | Data Type | Description & Usage |
|:-----:|:------------|:----------|:--------------------|
| 1 | `S No.` | Integer / String | Serial number within the sector workbook |
| 2 | `Title` | String | Official qualification / course title |
| 3 | `Code` | String | Official NQR qualification code (e.g., `2022/AA/AASSC/06397` or `QG-04-ES-00913-2023-V1-SCGJ`) |
| 4 | `Description` | String | Detailed synopsis of the job role, tasks, and responsibilities |
| 5 | `Sector Name` | String | Industry sector name (e.g., `Aerospace & Aviation`, `IT-ITeS`) |
| 6 | `Level` | Numeric (Decimal) | NSQF qualification level ranging from `1` to `7` (including half-levels: `2.5`, `3.5`, `4.5`, `5.5`, `6.5`) |
| 7 | `Maximum Notational Hours` | String / Int | Maximum training hours (e.g., `510`, `600`) |
| 8 | `Minimum Notational Hours` | String / Int | Minimum training hours |
| 9 | `Version` | String | Qualification pack version (e.g., `1.0`, `2.0`, `3.0`) |
| 10 | `Originally Approved` | Date String | Approval date by NCVET / NSQC |
| 11 | `Valid Till` | Date String | Expiration or validity date of the qualification |
| 12 | `Awarding Body` | String | Sector Skill Council (SSC) or awarding authority |
| 13 | `Certifying Bodies` | String | Designated certifying institutions |
| 14 | `Proposed Occupation` | String | NCO / National Classification of Occupations job role |
| 15 | `Progression Pathway` | String | Career and educational progression vertical/horizontal mobility |
| 16 | `Qualifcation Type` | String | Type (e.g., `Regular`, `Special`, `Short Term`) |
| 17 | `Adopted Qualifcation` | String | Reference to parent/adopted qualification if applicable |
| 18 | `Training Delivery Hours` | String | Hours breakdown (classroom, practical, OJT) |

---

## 3. Sector Distribution (44 Sectors, 2,810 Courses)

Each workbook corresponds 1:1 to an industry sector:

| # | Sector Name | Course Count | Primary Awarding Body / Council |
|---|:---|:---:|:---|
| 1 | IT-ITeS | 316 | NASSCOM / IT-ITeS SSC |
| 2 | Electronics & HW | 234 | Electronics Sector Skills Council of India (ESSCI) |
| 3 | Persons with Disability | 231 | Skill Council for Persons with Disability (SCPwD) |
| 4 | Agriculture | 185 | Agriculture Skill Council of India (ASCI) |
| 5 | Handicrafts & Carpets | 139 | Handicrafts and Carpet SSC |
| 6 | Apparel | 133 | Apparel Made-ups & Home Furnishing SSC |
| 7 | Media & Entertainment | 129 | Media & Entertainment Skills Council (MESC) |
| 8 | Tourism & Hospitality | 122 | Tourism and Hospitality SSC (THSC) |
| 9 | Automotive | 102 | Automotive Skills Development Council (ASDC) |
| 10 | Healthcare | 96 | Healthcare SSC |
| 11 | Life Sciences | 93 | Life Sciences Sector Skill Development Council |
| 12 | Textile & Handlooms | 93 | Textile Sector Skill Council |
| 13 | Construction | 89 | Construction Skill Development Council of India |
| 14 | Retail | 84 | Retailers Association's Skill Council of India |
| 15 | BFSI | 82 | BFSI Sector Skill Council of India |
| 16 | Capital Goods | 78 | Capital Goods Skill Council (CGSC) |
| 17 | Telecom | 78 | Telecom Sector Skill Council (TSSC) |
| 18 | Food Processing | 67 | Food Industry Capacity & Skill Initiative (FICSI) |
| 19 | Beauty & Wellness | 63 | Beauty & Wellness Sector Skill Council |
| 20 | Power | 61 | Power Sector Skill Council |
| 21 | Mining | 59 | Skill Council for Mining Sector |
| 22 | Logistics | 54 | Logistics Sector Skill Council |
| 23 | Management | 45 | Management & Entrepreneurship and Professional SSC |
| 24 | Plumbing | 39 | Indian Plumbing Skills Council |
| 25 | Environmental Science | 38 | Skill Council for Green Jobs (SCGJ) |
| 26 | Sports | 37 | Sports, Physical Education, Fitness & Leisure SSC |
| 27 | Paints & Coatings | 31 | Paints and Coatings Skill Council |
| 28 | Leather | 30 | Leather Sector Skill Council |
| 29 | Hydrocarbon | 28 | Hydrocarbon Sector Skill Council |
| 30 | Iron & Steel | 28 | Indian Iron and Steel Sector Skill Council |
| 31 | Gem & Jewellery | 26 | Gem & Jewellery Skill Council of India |
| 32 | Infrastructure Equipment | 25 | Infrastructure Equipment Skill Council |
| 33 | Chemical | 24 | Chemicals and Petrochemicals SSC |
| 34 | Security | 23 | Security Sector Skill Development Council |
| 35 | Rubber | 23 | Rubber, Chemical & Petrochemical Skill Development Council |
| 36 | Aerospace & Aviation | 19 | Aerospace and Aviation SSC |
| 37 | Furniture & Fittings | 18 | Furniture & Fittings Skill Council |
| 38 | Water Management | 13 | Skill Council for Green Jobs / Water Sector |
| 39 | Renewable Energy | 12 | Skill Council for Green Jobs |
| 40 | Domestic Workers | 11 | Domestic Workers Sector Skill Council |
| 41 | Strategic Manufacturing | 7 | Strategic Manufacturing Skill Council |
| 42 | Instrumentation | 5 | Instrumentation Automation SSC |
| 43 | Forestry | 4 | Agriculture & Forestry SSC |
| 44 | Waste Management | 4 | Skill Council for Green Jobs |

**Total**: **2,810** Courses across **44** Sectors.

---

## 4. Excluded Sector Policy & Audit

The following 15 sectors are designated as strictly excluded from the recommendation catalog:
1. Judiciary
2. Indian Defence Forces
3. Legal Activities
4. Legislators
5. Musical Instruments
6. Optical Products
7. Postal Services
8. Printing
9. Public Administration
10. Railways
11. Real Estate
12. Religious Professionals
13. Shipping
14. Tobacco Industry
15. Unorganised Sector

**Audit Result**: **0** courses from these 15 excluded sectors exist in the supplied dataset. The ingestion pipeline actively enforces this exclusion list as a strict defensive filter against any future dataset additions.

---

## 5. NSQF Level Distribution

The dataset spans 12 distinct NSQF levels, including recognized half-levels:

| NSQF Level | Qualification Count | Percentage |
|:---:|:---:|:---:|
| **Level 1.0** | 14 | 0.50% |
| **Level 2.0** | 180 | 6.41% |
| **Level 2.5** | 117 | 4.16% |
| **Level 3.0** | 557 | 19.82% |
| **Level 3.5** | 126 | 4.48% |
| **Level 4.0** | 843 | 29.99% |
| **Level 4.5** | 263 | 9.36% |
| **Level 5.0** | 430 | 15.30% |
| **Level 5.5** | 118 | 4.20% |
| **Level 6.0** | 149 | 5.30% |
| **Level 6.5** | 8 | 0.28% |
| **Level 7.0** | 5 | 0.18% |
| **Total** | **2,810** | **100.0%** |

> **Architecture Decision**: The PostgreSQL schema column for `nsqf_level` MUST be `NUMERIC(3, 1)` rather than `INTEGER` to accurately represent decimal levels (2.5, 3.5, 4.5, 5.5, 6.5) without truncation.

---

## 6. Notional Hours Distribution

Notional training hours indicate the total learning time (theory, practical, on-the-job training). In the dataset:

| Notional Hours Range | Course Count | Percentage |
|:---|:---:|:---:|
| **1 – 200 hours** | 556 | 19.79% |
| **201 – 400 hours** | 576 | 20.50% |
| **401 – 600 hours** | 1,187 | 42.24% |
| **601 – 800 hours** | 225 | 8.01% |
| **801 – 1,000 hours** | 89 | 3.17% |
| **1,001 – 1,200 hours** | 71 | 2.53% |
| **1,201 – 2,400 hours** | 102 | 3.63% |
| **Above 2,401 hours** | 4 | 0.14% |
| **Total** | **2,810** | **100.0%** |

---

## 7. Persons with Disability (PwD) Applicability

* Dedicated Sector: `Persons with Disability` contains **231** courses.
* The SCPwD (Skill Council for Persons with Disability) customizes courses for specific disability types:
  - **VI**: Visual Impairment / Blindness / Low Vision
  - **SHI**: Speech and Hearing Impairment / Deaf / Hard of Hearing
  - **LD**: Locomotor Disability
  - **ID**: Intellectual Disability / Autism Spectrum Disorder (ASD)
* Titles in this sector explicitly state the target disability, e.g.:
  - `Solar Domestic Water Heating Technician (SHI)` (Code: `PWD/SGJ/Q0601`)
  - `Microfinance Executive (LD)` (Code: `PWD/BSC/Q2301`)
  - `Sewing Machine Operator (VI)` (Code: `PWD/AMH/Q0301`)
* Schema Implementation:
  - `is_pwd BOOLEAN DEFAULT false`
  - `pwd_categories TEXT[]` (e.g. `ARRAY['SHI']`, `ARRAY['LD']`, `ARRAY['VI']`)

---

## 8. Data Anomalies and Resolution

1. **Duplicate Qualification Code**:
   - Code: `QG-04-ES-00913-2023-V1-SCGJ`
   - Courses:
     1. `Junior Technician- Mechanized Sewer Cleaning` (Green Jobs, Level 4)
     2. `Material Recovery Facility (MRF) Micro - Entrepreneur` (Green Jobs, Level 4)
   - Resolution: Use surrogate primary key `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` rather than `q_code` as the primary key. `q_code` is indexed with a non-unique index. A composite unique constraint `(q_code, title)` ensures deterministic idempotency on ingestion.

2. **Unicode Ligatures and Encoding**:
   - Files contain typographic ligatures (e.g. `\ufb03` for "ffi" in words like "Office").
   - Resolution: Normalization function applies `unicodedata.normalize('NFKD', text)` to expand ligatures to ASCII sequences before database persistence.

---

## 9. Relational Database Design

Rather than mixing 2,810 NSQF qualifications into the prototype `opportunities` table (which represents live PM-AJAY beneficiary skilling schemes), we introduce a dedicated, normalized catalog layer:

1. `nsqf_sectors`: Sector master data (slug, name, course count, active status).
2. `nsqf_qualifications`: Authoritative course catalog (id, q_code, title, sector_id, nsqf_level, notional_hours, min/max hours, description, proposed_occupation, progression_pathway, awarding_body, certifying_bodies, is_pwd, pwd_categories, raw_metadata).
3. Backward compatibility: The existing `opportunities` table maintains a foreign reference `qp_code REFERENCES nsqf_qualifications(q_code)` so live training batches can link to authoritative NQR courses.
