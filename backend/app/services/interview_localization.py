"""
Utthan Backend - Multilingual Question Bank & Localization for Adaptive Interview.
Supports official languages including Hindi, English, Bengali, Tamil, Telugu, Marathi,
Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, and Urdu.
"""

from typing import Dict, List, Optional
from app.schemas.adaptive_interview import QuestionOption


STAGE_TITLES: Dict[str, Dict[str, str]] = {
    "location": {
        "en": "Location Verification",
        "hi": "स्थान सत्यापन",
        "bn": "অবস্থান যাচাইকরণ",
        "ta": "இருப்பிட சரிபார்ப்பு",
        "te": "ప్రాంత నిర్ధారణ",
        "mr": "स्थान पडताळणी",
    },
    "basic_profile": {
        "en": "Basic Profile",
        "hi": "व्यक्तिगत परिचय",
        "bn": "প্রাথমিক পরিচিতি",
        "ta": "அடிப்படை விவரங்கள்",
        "te": "ప్రాథమిక ప్రొఫైల్",
        "mr": "मूलभूत माहिती",
    },
    "education": {
        "en": "Educational Background",
        "hi": "शैक्षणिक योग्यता",
        "bn": "শিক্ষাগত যোগ্যতা",
        "ta": "கல்வித் தகுதி",
        "te": "విద్యార్హత",
        "mr": "शैक्षणिक पात्रता",
    },
    "vocational_training": {
        "en": "Vocational & Skill Training",
        "hi": "व्यावसायिक एवं कौशल प्रशिक्षण",
        "bn": "ভোকেশনাল ও দক্ষতা প্রশিক্ষণ",
        "ta": "தொழில் தொழிற்பயிற்சி",
        "te": "వృత్తి నైపుణ్య శిక్షణ",
        "mr": "व्यावसायिक व कौशल्य प्रशिक्षण",
    },
    "experience": {
        "en": "Work Experience",
        "hi": "कार्य अनुभव",
        "bn": "কাজের অভিজ্ঞতা",
        "ta": "பணி அனுபவம்",
        "te": "పని అనుభవం",
        "mr": "कामाचा अनुभव",
    },
    "sector": {
        "en": "Industry Sector Interest",
        "hi": "पसंदीदा कार्य क्षेत्र (Sector)",
        "bn": "পছন্দের কাজের ক্ষেত্র (Sector)",
        "ta": "விருப்பமான தொழில் துறை",
        "te": "ఆసక్తికర రంగం",
        "mr": "आवडीचे कार्यक्षेत्र",
    },
    "catalog_context": {
        "en": "Job Role Specialization",
        "hi": "विशिष्ट कार्य भूमिका (Job Role)",
        "bn": "নির্দিষ্ট কাজের ভূমিকা (Job Role)",
        "ta": "வேலை பங்கு விருப்பம்",
        "te": "ఉద్యోగ పాత్ర ఎంపిక",
        "mr": "कामाची भूमिका",
    },
    "competency_evidence": {
        "en": "Skills & Tool Familiarity",
        "hi": "व्यावहारिक हुनर एवं औजार",
        "bn": "ব্যবহারিক দক্ষতা ও যন্ত্রপাতি",
        "ta": "நடைமுறைத் திறன் மற்றும் கருவிகள்",
        "te": "నైపుణ్యాలు మరియు పరికరాలు",
        "mr": "कौशल्ये आणि साधने",
    },
    "capacity_hours": {
        "en": "Training Duration Preference",
        "hi": "प्रशिक्षण समय सीमा",
        "bn": "প্রশিক্ষণের সময়সীমা",
        "ta": "பயிற்சி கால அளவு",
        "te": "శిక్షణ వ్యవధి",
        "mr": "प्रशिक्षण कालावधी",
    },
    "pwd": {
        "en": "Inclusion & Accessibility",
        "hi": "दिव्यांगजन / विशेष सुविधा",
        "bn": "বিশেষ সুবিধা ও অন্তর্ভুক্তি",
        "ta": "உள்ளடக்கம் மற்றும் அணுகல்",
        "te": "ప్రత్యేక అవసరాలు",
        "mr": "समावेशकता आणि सुलभता",
    },
    "work_preferences": {
        "en": "Career Goal & Commute",
        "hi": "आजीविका लक्ष्य एवं दूरी",
        "bn": "জীবিকা লক্ষ্য ও যাতায়াত",
        "ta": "தொழில் இலக்கு மற்றும் பயணம்",
        "te": "కెరీర్ లక్ష్యం మరియు ప్రయాణం",
        "mr": "ध्येय आणि प्रवास",
    },
    "review": {
        "en": "Profile Review & Confirmation",
        "hi": "प्रोफाइल समीक्षा एवं पुष्टि",
        "bn": "প্রোফাইল পর্যালোচনা ও নিশ্চিতকরণ",
        "ta": "சுயவிவர மதிப்பாய்வு",
        "te": "ప్రొఫైల్ సమీక్ష",
        "mr": "माहिती पुनरावलोकन",
    }
}


def get_stage_title(stage: str, lang: str = "hi") -> str:
    titles = STAGE_TITLES.get(stage, {})
    return titles.get(lang) or titles.get("en") or stage.replace("_", " ").title()


def get_education_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="no_formal", label="अनौपचारिक शिक्षा / साक्षर (No formal schooling)", icon="🌱"),
            QuestionOption(value="5th_pass", label="5वीं पास (5th Class)", icon="🎒"),
            QuestionOption(value="8th_pass", label="8वीं पास (8th Class)", icon="🏫"),
            QuestionOption(value="10th_pass", label="10वीं पास / मैट्रिक (10th Class)", icon="🎓"),
            QuestionOption(value="12th_pass", label="12वीं पास / इंटरमीडिएट (12th Class)", icon="📚"),
            QuestionOption(value="iti_vocational", label="आईटीआई / वोकेशनल डिप्लोमा (ITI Certificate)", icon="🛠️"),
            QuestionOption(value="diploma", label="पॉलिटेक्निक / तकनीकी डिप्लोमा (Polytechnic Diploma)", icon="📐"),
            QuestionOption(value="graduate", label="स्नातक / ग्रेजुएट (Bachelor's Degree)", icon="🏛️"),
            QuestionOption(value="post_graduate", label="परास्नातक / उच्च शिक्षा (Post Graduate / Higher)", icon="🔬"),
            QuestionOption(value="previous_nsqf", label="पूर्व NSQF प्रमाण पत्र धारक (Prior NSQF Certified)", icon="📜"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="no_formal", label="প্রাতিষ্ঠানিক পড়াশোনা নেই (No formal schooling)", icon="🌱"),
            QuestionOption(value="5th_pass", label="৫ম শ্রেণী পাস (5th Class)", icon="🎒"),
            QuestionOption(value="8th_pass", label="৮ম শ্রেণী পাস (8th Class)", icon="🏫"),
            QuestionOption(value="10th_pass", label="১০ম শ্রেণী (মাধ্যমিক) পাস (10th Class)", icon="🎓"),
            QuestionOption(value="12th_pass", label="১২ম শ্রেণী (উচ্চমাধ্যমিক) পাস (12th Class)", icon="📚"),
            QuestionOption(value="iti_vocational", label="আইটিআই / ভোকেশনাল ডিপ্লোমা (ITI Certificate)", icon="🛠️"),
            QuestionOption(value="diploma", label="পলিটেকনিক / কারিগরি ডিপ্লোমা (Polytechnic Diploma)", icon="📐"),
            QuestionOption(value="graduate", label="স্নাতক / ডিগ্রিধারী (Graduate)", icon="🏛️"),
            QuestionOption(value="post_graduate", label="স্নাতকোত্তর বা তদূর্ধ্ব (Post Graduate)", icon="🔬"),
            QuestionOption(value="previous_nsqf", label="পূর্বতন NSQF সনদপত্র রয়েছে (Prior NSQF)", icon="📜"),
        ]
    else:
        return [
            QuestionOption(value="no_formal", label="No formal schooling / Literate", icon="🌱"),
            QuestionOption(value="5th_pass", label="5th Standard Pass", icon="🎒"),
            QuestionOption(value="8th_pass", label="8th Standard Pass", icon="🏫"),
            QuestionOption(value="10th_pass", label="10th Standard Pass (Matriculation)", icon="🎓"),
            QuestionOption(value="12th_pass", label="12th Standard Pass (Higher Secondary)", icon="📚"),
            QuestionOption(value="iti_vocational", label="ITI / Vocational Certificate (CTS/NTC)", icon="🛠️"),
            QuestionOption(value="diploma", label="Polytechnic / Technical Diploma", icon="📐"),
            QuestionOption(value="graduate", label="Graduate / Bachelor's Degree", icon="🏛️"),
            QuestionOption(value="post_graduate", label="Post Graduate / Higher Degree", icon="🔬"),
            QuestionOption(value="previous_nsqf", label="Holder of prior NSQF Qualification", icon="📜"),
        ]


def get_vocational_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="none", label="कोई औपचारिक व्यावसायिक प्रशिक्षण नहीं", icon="❌"),
            QuestionOption(value="iti_cts", label="आईटीआई / सीटीएस (ITI / CTS / NTC)", icon="🛠️"),
            QuestionOption(value="cits", label="सीआईटीएस / प्रशिक्षक प्रशिक्षण (CITS / Instructor)", icon="👨‍🏫"),
            QuestionOption(value="ats_nac", label="अपरेंटिस / एनएसी (Apprenticeship ATS / NAC)", icon="📜"),
            QuestionOption(value="short_term", label="शॉर्ट-टर्म पीएमकेवीवाई / स्किल इंडिया कोर्स", icon="⏱️"),
            QuestionOption(value="informal", label="पारंपरिक / पारिवारिक हुनर (अनौपचारिक)", icon="🏡"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="none", label="কোনো প্রাতিষ্ঠানিক প্রশিক্ষণ নেই", icon="❌"),
            QuestionOption(value="iti_cts", label="আইটিআই / সিটিএস (ITI / CTS / NTC)", icon="🛠️"),
            QuestionOption(value="cits", label="সিআইটিএস / শিক্ষক প্রশিক্ষণ (CITS)", icon="👨‍🏫"),
            QuestionOption(value="ats_nac", label="অ্যাপ্রেন্টিস / এনএসি (ATS / NAC)", icon="📜"),
            QuestionOption(value="short_term", label="স্বল্পমেয়াদী সরকারি স্কিল কোর্স (PMKVY)", icon="⏱️"),
            QuestionOption(value="informal", label="পারিবারিক বা স্থানীয় কাজের অভিজ্ঞতা", icon="🏡"),
        ]
    else:
        return [
            QuestionOption(value="none", label="No formal vocational training", icon="❌"),
            QuestionOption(value="iti_cts", label="ITI / Craftsmen Training (CTS / NTC)", icon="🛠️"),
            QuestionOption(value="cits", label="Craft Instructor Training (CITS)", icon="👨‍🏫"),
            QuestionOption(value="ats_nac", label="Apprenticeship (ATS / NAC)", icon="📜"),
            QuestionOption(value="short_term", label="Short Term Skilling (PMKVY / NSDC)", icon="⏱️"),
            QuestionOption(value="informal", label="Informal / Hereditary Work Practice", icon="🏡"),
        ]


def get_experience_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="0", label="नया / कोई पूर्व अनुभव नहीं (Fresher)", icon="🌱"),
            QuestionOption(value="0.5", label="6 महीने से कम का अनुभव (Under 6 months)", icon="⏳"),
            QuestionOption(value="1.5", label="1 से 2 वर्ष का व्यावहारिक अनुभव", icon="🔨"),
            QuestionOption(value="3.5", label="3 से 5 वर्ष का कार्य अनुभव", icon="⭐"),
            QuestionOption(value="6.0", label="5 वर्ष से अधिक का विशेषज्ञ अनुभव", icon="🏆"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="0", label="কোনো পূর্ব কাজের অভিজ্ঞতা নেই (Fresher)", icon="🌱"),
            QuestionOption(value="0.5", label="৬ মাসের কম সময়ের প্রাথমিক কাজ", icon="⏳"),
            QuestionOption(value="1.5", label="১ থেকে ২ বছরের কাজের অভিজ্ঞতা", icon="🔨"),
            QuestionOption(value="3.5", label="৩ থেকে ৫ বছরের কাজের অভিজ্ঞতা", icon="⭐"),
            QuestionOption(value="6.0", label="৫ বছরের বেশি অভিজ্ঞ দক্ষ কারিগর", icon="🏆"),
        ]
    else:
        return [
            QuestionOption(value="0", label="No prior work experience (Fresher)", icon="🌱"),
            QuestionOption(value="0.5", label="Under 6 months basic experience", icon="⏳"),
            QuestionOption(value="1.5", label="1 to 2 years practical experience", icon="🔨"),
            QuestionOption(value="3.5", label="3 to 5 years established experience", icon="⭐"),
            QuestionOption(value="6.0", label="Over 5 years experienced professional", icon="🏆"),
        ]


def get_notional_hours_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="1–200", label="अल्पकालिक क्रैश कोर्स (1–200 घंटे, ~1 माह)", icon="⚡"),
            QuestionOption(value="201–400", label="मध्यम अवधि प्रशिक्षण (201–400 घंटे, ~2-3 माह)", icon="📅"),
            QuestionOption(value="401–600", label="मानक पूर्णकालिक प्रमाण पत्र (401–600 घंटे, ~3-4 माह)", icon="📜"),
            QuestionOption(value="601–1200", label="विस्तृत तकनीकी प्रशिक्षण (601–1200 घंटे, ~6 माह)", icon="🎓"),
            QuestionOption(value="Above 1201", label="दीर्घकालिक डिप्लोमा / व्यापक कोर्स (1200+ घंटे, 1 वर्ष)", icon="🏛️"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="1–200", label="স্বল্পমেয়াদী কোর্স (১–২০০ ঘণ্টা, ~১ মাস)", icon="⚡"),
            QuestionOption(value="201–400", label="মাঝারি প্রশিক্ষণ (২০১–৪০০ ঘণ্টা, ~২-৩ মাস)", icon="📅"),
            QuestionOption(value="401–600", label="স্ট্যান্ডার্ড ফুল-টাইম কোর্স (৪০১–৬০০ ঘণ্টা, ~৩-৪ মাস)", icon="📜"),
            QuestionOption(value="601–1200", label="গভীর কারিগরি প্রশিক্ষণ (৬০১–১২০০ ঘণ্টা, ~৬ মাস)", icon="🎓"),
            QuestionOption(value="Above 1201", label="দীর্ঘমেয়াদী ডিপ্লোমা (১২০০+ ঘণ্টা, ১ বছর)", icon="🏛️"),
        ]
    else:
        return [
            QuestionOption(value="1–200", label="Short crash training (1–200 hours, ~1 month)", icon="⚡"),
            QuestionOption(value="201–400", label="Medium foundation (201–400 hours, ~2-3 months)", icon="📅"),
            QuestionOption(value="401–600", label="Standard qualification (401–600 hours, ~3-4 months)", icon="📜"),
            QuestionOption(value="601–1200", label="Comprehensive skilling (601–1200 hours, ~6 months)", icon="🎓"),
            QuestionOption(value="Above 1201", label="Advanced diploma (Above 1200 hours, ~1 year)", icon="🏛️"),
        ]


def get_pwd_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="none", label="नहीं (General / No Disability)", icon="✅"),
            QuestionOption(value="LD", label="अस्थि दिव्यांगता (Locomotor Disability / Orthopedic)", icon="🦿"),
            QuestionOption(value="SHI", label="मूक एवं बधिर (Speech & Hearing Impairment)", icon="🦻"),
            QuestionOption(value="VI", label="दृष्टिबाधित / कम दृष्टि (Visual Impairment / Blindness)", icon="👁️"),
            QuestionOption(value="ID", label="बौद्धिक या विकास संबंधी (Intellectual / Neurodiverse)", icon="🧠"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="none", label="না (General / No Disability)", icon="✅"),
            QuestionOption(value="LD", label="শারীরিক বা চলাফেরার প্রতিবন্ধকতা (Locomotor Disability)", icon="🦿"),
            QuestionOption(value="SHI", label="বাক ও শ্রবণ প্রতিবন্ধকতা (Speech & Hearing)", icon="🦻"),
            QuestionOption(value="VI", label="দৃষ্টিহীনতা বা ক্ষীণদৃষ্টি (Visual Impairment)", icon="👁️"),
            QuestionOption(value="ID", label="বৌদ্ধিক প্রতিবন্ধকতা (Intellectual Disability)", icon="🧠"),
        ]
    else:
        return [
            QuestionOption(value="none", label="No Disability (General candidate)", icon="✅"),
            QuestionOption(value="LD", label="Locomotor Disability (Physical / Movement)", icon="🦿"),
            QuestionOption(value="SHI", label="Speech & Hearing Impairment (Deaf / Hard of Hearing)", icon="🦻"),
            QuestionOption(value="VI", label="Visual Impairment (Blind / Low Vision)", icon="👁️"),
            QuestionOption(value="ID", label="Intellectual / Neurodivergent Disability", icon="🧠"),
        ]


def get_mobility_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="village_block", label="अपने गाँव या ब्लॉक के अंदर (Village / Block)", icon="🏡"),
            QuestionOption(value="within_15km", label="15 किमी तक नजदीकी कस्बा / बाजार (Up to 15 km)", icon="🚲"),
            QuestionOption(value="district_wide", label="अपने पूरे जिले में कहीं भी (Anywhere in District)", icon="🚌"),
            QuestionOption(value="relocate_hostel", label="हॉस्टल/आवास मिले तो बाहर जाने को तैयार (Relocate)", icon="🎒"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="village_block", label="নিজের গ্রাম বা ব্লকের মধ্যে (Village / Block)", icon="🏡"),
            QuestionOption(value="within_15km", label="১৫ কিমি পর্যন্ত কাছের শহর বা বাজার (Up to 15 km)", icon="🚲"),
            QuestionOption(value="district_wide", label="জেলার যেকোনো জায়গায় (District-wide)", icon="🚌"),
            QuestionOption(value="relocate_hostel", label="থাকার ব্যবস্থা থাকলে বাইরে যেতে প্রস্তুত (Relocate)", icon="🎒"),
        ]
    else:
        return [
            QuestionOption(value="village_block", label="Within own village or block", icon="🏡"),
            QuestionOption(value="within_15km", label="Up to 15 km (Nearby market or town)", icon="🚲"),
            QuestionOption(value="district_wide", label="Anywhere in the district", icon="🚌"),
            QuestionOption(value="relocate_hostel", label="Willing to relocate if hostel provided", icon="🎒"),
        ]


def get_goal_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="training_stipend", label="प्रमाणित सरकारी ट्रेनिंग + मासिक वजीफा (Stipend)", icon="📜"),
            QuestionOption(value="job_placement", label="नजदीकी क्षेत्र में तुरंत पक्की नौकरी (Job Placement)", icon="💼"),
            QuestionOption(value="micro_business", label="अपनी खुद की दुकान या व्यवसाय शुरू करना (Self-employed)", icon="🏪"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="training_stipend", label="সার্টিফিকেট প্রশিক্ষণ + মাসিক বৃত্তি (Stipend)", icon="📜"),
            QuestionOption(value="job_placement", label="এলাকায় দ্রুত চাকরির সুযোগ (Job Placement)", icon="💼"),
            QuestionOption(value="micro_business", label="নিজের ছোট ব্যবসা বা দোকান শুরু করা (Micro-business)", icon="🏪"),
        ]
    else:
        return [
            QuestionOption(value="training_stipend", label="Certified Training + Monthly Stipend", icon="📜"),
            QuestionOption(value="job_placement", label="Immediate Local Job Placement", icon="💼"),
            QuestionOption(value="micro_business", label="Start My Own Micro-Business / Shop", icon="🏪"),
        ]
