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
    "capacity_hours": {
        "en": "Training Duration Preference",
        "hi": "प्रशिक्षण समय सीमा (Notional Hours)",
        "bn": "প্রশিক্ষণের সময়সীমা",
        "ta": "பயிற்சி கால அளவு",
        "te": "శిక్షణ వ్యవధి",
        "mr": "प्रशिक्षण कालावधी",
    },
    "pwd": {
        "en": "Inclusion & Accessibility",
        "hi": "दिव्यांगजन / विशेष सुविधा (PwD)",
        "bn": "বিশেষ সুবিধা ও অন্তর্ভুক্তি",
        "ta": "உள்ளடக்கம் மற்றும் அணுகல்",
        "te": "ప్రత్యేక అవసరాలు",
        "mr": "समावेशकता आणि सुलभता",
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
    },
}


def get_stage_title(stage: str, lang: str = "hi") -> str:
    titles = STAGE_TITLES.get(stage, {})
    return titles.get(lang) or titles.get("en") or stage.replace("_", " ").title()


def get_education_options(lang: str = "hi") -> List[QuestionOption]:
    """
    Returns full canonical education options matching NSQF/NQR catalog standards:
    None, No formal education, Ability to read/write, 5th, 6th, 7th, 8th, 9th, 10th, 11th, 12th,
    Diploma, 1st year diploma, UG diploma, Graduate, UG, Post Graduate, PhD, Previous NSQF qualification,
    and ITI instructor / CITS / CTS / ATS.
    """
    if lang == "hi":
        return [
            QuestionOption(value="none", label="कोई औपचारिक शिक्षा नहीं (None)", icon="🌱"),
            QuestionOption(value="no_formal", label="अनौपचारिक शिक्षा (No formal schooling)", icon="🌱"),
            QuestionOption(value="literate_read_write", label="पढ़ने-लिखने में सक्षम / बुनियादी साक्षर (Literate / Read & Write)", icon="✏️"),
            QuestionOption(value="5th", label="5वीं पास (5th Class)", icon="🎒"),
            QuestionOption(value="6th", label="6वीं पास (6th Class)", icon="🎒"),
            QuestionOption(value="7th", label="7वीं पास (7th Class)", icon="🎒"),
            QuestionOption(value="8th", label="8वीं पास (8th Class)", icon="🏫"),
            QuestionOption(value="9th", label="9वीं पास (9th Class)", icon="🏫"),
            QuestionOption(value="10th", label="10वीं पास / मैट्रिक (10th Class / Matric)", icon="🎓"),
            QuestionOption(value="11th", label="11वीं पास (11th Class)", icon="📚"),
            QuestionOption(value="12th", label="12वीं पास / इंटरमीडिएट (12th Class / Intermediate)", icon="📚"),
            QuestionOption(value="1st_year_diploma", label="पॉलिटेक्निक प्रथम वर्ष (1st Year Diploma)", icon="📐"),
            QuestionOption(value="ug_diploma", label="यूजी डिप्लोमा / व्यावसायिक डिप्लोमा (UG Diploma)", icon="📐"),
            QuestionOption(value="diploma", label="तकनीकी डिप्लोमा (3-Year Polytechnic Diploma)", icon="📐"),
            QuestionOption(value="ug", label="कॉलेज अध्ययनरत / अंडरग्रेजुएट (UG Pursuing)", icon="🏛️"),
            QuestionOption(value="graduate", label="स्नातक / ग्रेजुएट (Bachelor's Degree)", icon="🏛️"),
            QuestionOption(value="post_graduate", label="परास्नातक / मास्टर डिग्री (Post Graduate / Master's)", icon="🔬"),
            QuestionOption(value="phd", label="पीएचडी / डॉक्टरेट (PhD / Doctorate)", icon="🔬"),
            QuestionOption(value="previous_nsqf", label="पूर्व NSQF प्रमाण पत्र धारक (Prior NSQF Qualification)", icon="📜"),
            QuestionOption(value="iti_instructor_cits", label="आईटीआई प्रशिक्षक / सीआईटीएस / सीटीएस धारक (ITI Instructor / CITS / CTS)", icon="🛠️"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="none", label="কোনো প্রাতিষ্ঠানিক শিক্ষা নেই (None)", icon="🌱"),
            QuestionOption(value="no_formal", label="অনানুষ্ঠানিক শিক্ষা (No formal schooling)", icon="🌱"),
            QuestionOption(value="literate_read_write", label="পড়তে ও লিখতে সক্ষম / প্রাথমিক সাক্ষর (Literate)", icon="✏️"),
            QuestionOption(value="5th", label="৫ম শ্রেণী পাস (5th Class)", icon="🎒"),
            QuestionOption(value="6th", label="৬ষ্ঠ শ্রেণী পাস (6th Class)", icon="🎒"),
            QuestionOption(value="7th", label="৭ম শ্রেণী পাস (7th Class)", icon="🎒"),
            QuestionOption(value="8th", label="৮ম শ্রেণী পাস (8th Class)", icon="🏫"),
            QuestionOption(value="9th", label="৯ম শ্রেণী পাস (9th Class)", icon="🏫"),
            QuestionOption(value="10th", label="১০ম শ্রেণী (মাধ্যমিক) পাস (10th Class / Matric)", icon="🎓"),
            QuestionOption(value="11th", label="১১শ শ্রেণী পাস (11th Class)", icon="📚"),
            QuestionOption(value="12th", label="১২শ শ্রেণী (উচ্চমাধ্যমিক) পাস (12th Class)", icon="📚"),
            QuestionOption(value="1st_year_diploma", label="পলিটেকনিক প্রথম বর্ষ (1st Year Diploma)", icon="📐"),
            QuestionOption(value="ug_diploma", label="ইউজি ডিপ্লোমা (UG Diploma)", icon="📐"),
            QuestionOption(value="diploma", label="কারিগরি ডিপ্লোমা (Polytechnic Diploma)", icon="📐"),
            QuestionOption(value="ug", label="কলেজ অধ্যয়নরত (Undergraduate Student)", icon="🏛️"),
            QuestionOption(value="graduate", label="স্নাতক / ডিগ্রিধারী (Graduate / Bachelor's)", icon="🏛️"),
            QuestionOption(value="post_graduate", label="স্নাতকোত্তর (Post Graduate / Master's)", icon="🔬"),
            QuestionOption(value="phd", label="পিএইচডি বা ডক্টরেট (PhD / Doctorate)", icon="🔬"),
            QuestionOption(value="previous_nsqf", label="পূর্বতন NSQF সনদপত্র রয়েছে (Prior NSQF)", icon="📜"),
            QuestionOption(value="iti_instructor_cits", label="আইটিআই প্রশিক্ষক / সিআইটিএস / সিটিএস (CITS / CTS Instructor)", icon="🛠️"),
        ]
    else:
        return [
            QuestionOption(value="none", label="None / No Education", icon="🌱"),
            QuestionOption(value="no_formal", label="No formal schooling / Informal", icon="🌱"),
            QuestionOption(value="literate_read_write", label="Ability to read and write / Basic Literacy", icon="✏️"),
            QuestionOption(value="5th", label="5th Standard Pass", icon="🎒"),
            QuestionOption(value="6th", label="6th Standard Pass", icon="🎒"),
            QuestionOption(value="7th", label="7th Standard Pass", icon="🎒"),
            QuestionOption(value="8th", label="8th Standard Pass", icon="🏫"),
            QuestionOption(value="9th", label="9th Standard Pass", icon="🏫"),
            QuestionOption(value="10th", label="10th Standard Pass (Matriculation)", icon="🎓"),
            QuestionOption(value="11th", label="11th Standard Pass", icon="📚"),
            QuestionOption(value="12th", label="12th Standard Pass (Higher Secondary)", icon="📚"),
            QuestionOption(value="1st_year_diploma", label="1st Year Polytechnic Diploma", icon="📐"),
            QuestionOption(value="ug_diploma", label="Undergraduate / Vocational Diploma", icon="📐"),
            QuestionOption(value="diploma", label="3-Year Polytechnic / Technical Diploma", icon="📐"),
            QuestionOption(value="ug", label="Undergraduate (College Pursuing)", icon="🏛️"),
            QuestionOption(value="graduate", label="Graduate / Bachelor's Degree", icon="🏛️"),
            QuestionOption(value="post_graduate", label="Post Graduate / Master's Degree", icon="🔬"),
            QuestionOption(value="phd", label="PhD / Doctorate", icon="🔬"),
            QuestionOption(value="previous_nsqf", label="Holder of prior NSQF Qualification", icon="📜"),
            QuestionOption(value="iti_instructor_cits", label="ITI Instructor / CITS / CTS / ATS Certified", icon="🛠️"),
        ]


def get_vocational_options(lang: str = "hi") -> List[QuestionOption]:
    """
    Returns vocational and skill training options covering official NCVET categories:
    None, CTS/NTC, CITS, ATS, NAC, ITI, DST, Flexi MOU, NTC/CITS, NTC/NAC/CITS,
    2-year NTC, 1-year CTS, NTC/NAC, NTC, Equivalent, and Short Term.
    """
    if lang == "hi":
        return [
            QuestionOption(value="none", label="कोई नहीं (None)", icon="❌"),
            QuestionOption(value="iti", label="आईटीआई (Industrial Training Institute - ITI)", icon="🛠️"),
            QuestionOption(value="cts_ntc", label="सीटीएस / एनटीसी (Craftsmen Training Scheme / NTC)", icon="⚙️"),
            QuestionOption(value="2_year_ntc", label="2-वर्षीय एनटीसी प्रमाण पत्र (2-Year NTC)", icon="📜"),
            QuestionOption(value="1_year_cts", label="1-वर्षीय सीटीएस प्रमाण पत्र (1-Year CTS)", icon="📜"),
            QuestionOption(value="cits", label="सीआईटीएस / क्राफ्ट इंस्ट्रक्टर (CITS Instructor)", icon="👨‍🏫"),
            QuestionOption(value="ats", label="अपरेंटिस प्रशिक्षण योजना (ATS - Apprenticeship)", icon="🏭"),
            QuestionOption(value="nac", label="राष्ट्रीय अपरेंटिस प्रमाणपत्र (NAC - National Apprenticeship)", icon="🏆"),
            QuestionOption(value="dst", label="दोहरी प्रशिक्षण प्रणाली (DST - Dual System of Training)", icon="🤝"),
            QuestionOption(value="flexi_mou", label="फ्लेक्सी एमओयू उद्योग आधारित प्रशिक्षण (Flexi MOU)", icon="🏢"),
            QuestionOption(value="ntc_cits", label="एनटीसी एवं सीआईटीएस संयुक्त (NTC + CITS)", icon="🏅"),
            QuestionOption(value="ntc_nac_cits", label="एनटीसी + एनएसी + सीआईटीएस (NTC + NAC + CITS)", icon="🌟"),
            QuestionOption(value="ntc_nac", label="एनटीसी एवं एनएसी (NTC + NAC)", icon="📜"),
            QuestionOption(value="short_term", label="शॉर्ट-टर्म पीएमकेवीवाई / स्किल इंडिया (Short Term Skilling)", icon="⏱️"),
            QuestionOption(value="equivalent", label="समकक्ष व्यावसायिक योग्यता (Equivalent)", icon="🔧"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="none", label="কোনোটিই নয় (None)", icon="❌"),
            QuestionOption(value="iti", label="আইটিআই (Industrial Training Institute - ITI)", icon="🛠️"),
            QuestionOption(value="cts_ntc", label="সিটিএস / এনটিসি (CTS / NTC)", icon="⚙️"),
            QuestionOption(value="2_year_ntc", label="২-বছরের এনটিসি (2-Year NTC)", icon="📜"),
            QuestionOption(value="1_year_cts", label="১-বছরের সিটিএস (1-Year CTS)", icon="📜"),
            QuestionOption(value="cits", label="সিআইটিএস কারিগরি শিক্ষক প্রশিক্ষণ (CITS)", icon="👨‍🏫"),
            QuestionOption(value="ats", label="অ্যাপ্রেন্টিসশিপ ট্রেনিং (ATS)", icon="🏭"),
            QuestionOption(value="nac", label="ন্যাশনাল অ্যাপ্রেন্টিসশিপ সার্টিফিকেট (NAC)", icon="🏆"),
            QuestionOption(value="dst", label="ডুয়াল সিস্টেম ট্রেনিং (DST)", icon="🤝"),
            QuestionOption(value="flexi_mou", label="ফ্লেক্সি মৌ ইন্ডাস্ট্রি ট্রেনিং (Flexi MOU)", icon="🏢"),
            QuestionOption(value="ntc_cits", label="এনটিসি ও সিআইটিএস (NTC + CITS)", icon="🏅"),
            QuestionOption(value="ntc_nac_cits", label="এনটিসি + এনএসি + সিআইটিএস (NTC + NAC + CITS)", icon="🌟"),
            QuestionOption(value="ntc_nac", label="এনটিসি ও এনএসি (NTC + NAC)", icon="📜"),
            QuestionOption(value="short_term", label="স্বল্পমেয়াদী সরকারি স্কিল কোর্স (PMKVY)", icon="⏱️"),
            QuestionOption(value="equivalent", label="সমমানের কারিগরি যোগ্যতা (Equivalent)", icon="🔧"),
        ]
    else:
        return [
            QuestionOption(value="none", label="None", icon="❌"),
            QuestionOption(value="iti", label="Industrial Training Institute (ITI)", icon="🛠️"),
            QuestionOption(value="cts_ntc", label="Craftsmen Training Scheme / NTC (CTS/NTC)", icon="⚙️"),
            QuestionOption(value="2_year_ntc", label="2-Year National Trade Certificate (2-year NTC)", icon="📜"),
            QuestionOption(value="1_year_cts", label="1-Year Craftsmen Training (1-year CTS)", icon="📜"),
            QuestionOption(value="cits", label="Craft Instructor Training Scheme (CITS)", icon="👨‍🏫"),
            QuestionOption(value="ats", label="Apprenticeship Training Scheme (ATS)", icon="🏭"),
            QuestionOption(value="nac", label="National Apprenticeship Certificate (NAC)", icon="🏆"),
            QuestionOption(value="dst", label="Dual System of Training (DST)", icon="🤝"),
            QuestionOption(value="flexi_mou", label="Industry Flexi MOU Training", icon="🏢"),
            QuestionOption(value="ntc_cits", label="Combined NTC + CITS", icon="🏅"),
            QuestionOption(value="ntc_nac_cits", label="Combined NTC + NAC + CITS", icon="🌟"),
            QuestionOption(value="ntc_nac", label="Combined NTC + NAC", icon="📜"),
            QuestionOption(value="short_term", label="Short Term Skilling (PMKVY / NSDC)", icon="⏱️"),
            QuestionOption(value="equivalent", label="Equivalent Vocational Training", icon="🔧"),
        ]


def get_experience_options(lang: str = "hi") -> List[QuestionOption]:
    """
    Returns work experience duration options supporting 0 to 12+ years with half-year granularity.
    """
    if lang == "hi":
        return [
            QuestionOption(value="0", label="कोई पूर्व अनुभव नहीं (No experience / Fresher)", icon="🌱"),
            QuestionOption(value="0.5", label="6 महीने का अनुभव (6 Months)", icon="⏳"),
            QuestionOption(value="1.0", label="1 वर्ष का अनुभव (1 Year)", icon="🔨"),
            QuestionOption(value="1.5", label="1.5 वर्ष का अनुभव (1.5 Years)", icon="🔨"),
            QuestionOption(value="2.0", label="2 वर्ष का अनुभव (2 Years)", icon="🔨"),
            QuestionOption(value="3.0", label="3 वर्ष का अनुभव (3 Years)", icon="⭐"),
            QuestionOption(value="4.0", label="4 वर्ष का अनुभव (4 Years)", icon="⭐"),
            QuestionOption(value="5.0", label="5 वर्ष का अनुभव (5 Years)", icon="⭐"),
            QuestionOption(value="6.0", label="6 वर्ष का अनुभव (6 Years)", icon="🏆"),
            QuestionOption(value="7.0", label="7 वर्ष का अनुभव (7 Years)", icon="🏆"),
            QuestionOption(value="8.0", label="8 वर्ष का अनुभव (8 Years)", icon="🏆"),
            QuestionOption(value="9.0", label="9 वर्ष का अनुभव (9 Years)", icon="🏆"),
            QuestionOption(value="10.0", label="10 वर्ष का अनुभव (10 Years)", icon="👑"),
            QuestionOption(value="11.0", label="11 वर्ष का अनुभव (11 Years)", icon="👑"),
            QuestionOption(value="12.0", label="12 वर्ष का अनुभव (12 Years)", icon="👑"),
            QuestionOption(value="13.0", label="12 वर्ष से अधिक का विशेषज्ञ अनुभव (12+ Years)", icon="👑"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="0", label="কোনো কাজের অভিজ্ঞতা নেই (No experience / Fresher)", icon="🌱"),
            QuestionOption(value="0.5", label="৬ মাসের অভিজ্ঞতা (6 Months)", icon="⏳"),
            QuestionOption(value="1.0", label="১ বছরের অভিজ্ঞতা (1 Year)", icon="🔨"),
            QuestionOption(value="1.5", label="১.৫ বছরের অভিজ্ঞতা (1.5 Years)", icon="🔨"),
            QuestionOption(value="2.0", label="২ বছরের অভিজ্ঞতা (2 Years)", icon="🔨"),
            QuestionOption(value="3.0", label="৩ বছরের অভিজ্ঞতা (3 Years)", icon="⭐"),
            QuestionOption(value="4.0", label="৪ বছরের অভিজ্ঞতা (4 Years)", icon="⭐"),
            QuestionOption(value="5.0", label="৫ বছরের অভিজ্ঞতা (5 Years)", icon="⭐"),
            QuestionOption(value="6.0", label="৬ বছরের অভিজ্ঞতা (6 Years)", icon="🏆"),
            QuestionOption(value="7.0", label="৭ বছরের অভিজ্ঞতা (7 Years)", icon="🏆"),
            QuestionOption(value="8.0", label="৮ বছরের অভিজ্ঞতা (8 Years)", icon="🏆"),
            QuestionOption(value="9.0", label="৯ বছরের অভিজ্ঞতা (9 Years)", icon="🏆"),
            QuestionOption(value="10.0", label="১০ বছরের অভিজ্ঞতা (10 Years)", icon="👑"),
            QuestionOption(value="11.0", label="১১ বছরের অভিজ্ঞতা (11 Years)", icon="👑"),
            QuestionOption(value="12.0", label="১২ বছরের অভিজ্ঞতা (12 Years)", icon="👑"),
            QuestionOption(value="13.0", label="১২ বছরের বেশি দীর্ঘ অভিজ্ঞতা (12+ Years)", icon="👑"),
        ]
    else:
        return [
            QuestionOption(value="0", label="No experience (Fresher)", icon="🌱"),
            QuestionOption(value="0.5", label="6 Months experience", icon="⏳"),
            QuestionOption(value="1.0", label="1 Year practical experience", icon="🔨"),
            QuestionOption(value="1.5", label="1.5 Years practical experience", icon="🔨"),
            QuestionOption(value="2.0", label="2 Years experience", icon="🔨"),
            QuestionOption(value="3.0", label="3 Years experience", icon="⭐"),
            QuestionOption(value="4.0", label="4 Years experience", icon="⭐"),
            QuestionOption(value="5.0", label="5 Years experience", icon="⭐"),
            QuestionOption(value="6.0", label="6 Years experience", icon="🏆"),
            QuestionOption(value="7.0", label="7 Years experience", icon="🏆"),
            QuestionOption(value="8.0", label="8 Years experience", icon="🏆"),
            QuestionOption(value="9.0", label="9 Years experience", icon="🏆"),
            QuestionOption(value="10.0", label="10 Years seasoned experience", icon="👑"),
            QuestionOption(value="11.0", label="11 Years seasoned experience", icon="👑"),
            QuestionOption(value="12.0", label="12 Years master experience", icon="👑"),
            QuestionOption(value="13.0", label="Above 12 Years master craftsman", icon="👑"),
        ]


def get_notional_hours_options(lang: str = "hi") -> List[QuestionOption]:
    """
    Returns exact 8 catalog-grounded notional hours buckets:
    1–200, 201–400, 401–600, 601–800, 801–1000, 1001–1200, 1201–2400, Above 2401.
    """
    if lang == "hi":
        return [
            QuestionOption(value="1–200", label="1–200 घंटे (अल्पकालिक क्रैश कोर्स, ~1 माह)", icon="⚡"),
            QuestionOption(value="201–400", label="201–400 घंटे (फाउंडेशन कोर्स, ~2-3 माह)", icon="📅"),
            QuestionOption(value="401–600", label="401–600 घंटे (मानक कौशल प्रमाण पत्र, ~3-4 माह)", icon="📜"),
            QuestionOption(value="601–800", label="601–800 घंटे (विस्तृत व्यावहारिक कोर्स, ~5 माह)", icon="🔨"),
            QuestionOption(value="801–1000", label="801–1000 घंटे (उन्नत व्यावसायिक कोर्स, ~6-7 माह)", icon="🎓"),
            QuestionOption(value="1001–1200", label="1001–1200 घंटे (गहन तकनीकी कोर्स, ~8-9 माह)", icon="⚙️"),
            QuestionOption(value="1201–2400", label="1201–2400 घंटे (दीर्घकालिक डिप्लोमा, ~1-2 वर्ष)", icon="🏛️"),
            QuestionOption(value="Above 2401", label="2401+ घंटे (व्यापक बहु-वर्षीय तकनीकी कार्यक्रम)", icon="🔬"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="1–200", label="১–২০০ ঘণ্টা (স্বল্পমেয়াদী ক্র্যাশ কোর্স, ~১ মাস)", icon="⚡"),
            QuestionOption(value="201–400", label="২০১–৪০০ ঘণ্টা (ফাউন্ডেশন কোর্স, ~২-৩ মাস)", icon="📅"),
            QuestionOption(value="401–600", label="৪০১–৬০০ ঘণ্টা (স্ট্যান্ডার্ড স্কিল কোর্স, ~৩-৪ মাস)", icon="📜"),
            QuestionOption(value="601–800", label="৬০১–৮০০ ঘণ্টা (বিস্তারিত ব্যবহারিক কোর্স, ~৫ মাস)", icon="🔨"),
            QuestionOption(value="801–1000", label="৮০১–১০০০ ঘণ্টা (উন্নত বৃত্তিমূলক কোর্স, ~৬-৭ মাস)", icon="🎓"),
            QuestionOption(value="1001–1200", label="১০০১–১২০০ ঘণ্টা (গভীর কারিগরি কোর্স, ~৮-৯ মাস)", icon="⚙️"),
            QuestionOption(value="1201–2400", label="১২০১–২৪০০ ঘণ্টা (দীর্ঘমেয়াদী ডিপ্লোমা, ~১-২ বছর)", icon="🏛️"),
            QuestionOption(value="Above 2401", label="২৪০১+ ঘণ্টা (বহু-বর্ষীয় ব্যাপক টেকনিক্যাল প্রোগ্রাম)", icon="🔬"),
        ]
    else:
        return [
            QuestionOption(value="1–200", label="1–200 Hours (Short crash training, ~1 month)", icon="⚡"),
            QuestionOption(value="201–400", label="201–400 Hours (Foundation skill training, ~2-3 months)", icon="📅"),
            QuestionOption(value="401–600", label="401–600 Hours (Standard qualification, ~3-4 months)", icon="📜"),
            QuestionOption(value="601–800", label="601–800 Hours (Comprehensive practical, ~5 months)", icon="🔨"),
            QuestionOption(value="801–1000", label="801–1000 Hours (Advanced vocational, ~6-7 months)", icon="🎓"),
            QuestionOption(value="1001–1200", label="1001–1200 Hours (Intensive technical, ~8-9 months)", icon="⚙️"),
            QuestionOption(value="1201–2400", label="1201–2400 Hours (Long-term diploma, ~1-2 years)", icon="🏛️"),
            QuestionOption(value="Above 2401", label="Above 2401 Hours (Comprehensive multi-year program)", icon="🔬"),
        ]


def get_pwd_options(lang: str = "hi") -> List[QuestionOption]:
    """
    Returns PwD options covering the catalog-supported categories:
    VI (Visual Impairment), SHI (Speech & Hearing Impairment),
    LD (Locomotor Disability), ID (Intellectual Disability).
    """
    if lang == "hi":
        return [
            QuestionOption(value="none", label="नहीं (General / No Disability)", icon="✅"),
            QuestionOption(value="LD", label="अस्थि दिव्यांगता (Locomotor Disability / LD)", icon="🦿", description="चलने-फिरने या हाथ-पैर में गतिशीलता संबंधी"),
            QuestionOption(value="SHI", label="मूक एवं बधिर (Speech & Hearing Impairment / SHI)", icon="🦻", description="बोलने एवं सुनने में सहायता की आवश्यकता"),
            QuestionOption(value="VI", label="दृष्टिबाधित / कम दृष्टि (Visual Impairment / VI)", icon="👁️", description="नेत्रहीन या कम दृष्टि वाले शिक्षार्थी"),
            QuestionOption(value="ID", label="बौद्धिक या विकास संबंधी (Intellectual Disability / ID)", icon="🧠", description="सीखने एवं संज्ञानात्मक सहयोग"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="none", label="না (General / No Disability)", icon="✅"),
            QuestionOption(value="LD", label="শারীরিক বা চলাফেরার প্রতিবন্ধকতা (Locomotor Disability / LD)", icon="🦿"),
            QuestionOption(value="SHI", label="বাক ও শ্রবণ প্রতিবন্ধকতা (Speech & Hearing / SHI)", icon="🦻"),
            QuestionOption(value="VI", label="দৃষ্টিহীনতা বা ক্ষীণদৃষ্টি (Visual Impairment / VI)", icon="👁️"),
            QuestionOption(value="ID", label="বৌদ্ধিক প্রতিবন্ধকতা (Intellectual Disability / ID)", icon="🧠"),
        ]
    else:
        return [
            QuestionOption(value="none", label="General / No Disability", icon="✅"),
            QuestionOption(value="LD", label="Locomotor Disability (LD / Orthopedic)", icon="🦿", description="Mobility, physical, or dexterity assistance"),
            QuestionOption(value="SHI", label="Speech & Hearing Impairment (SHI / Deaf / Hard of Hearing)", icon="🦻", description="Sign language or audio assistance required"),
            QuestionOption(value="VI", label="Visual Impairment (VI / Blind / Low Vision)", icon="👁️", description="Screen reader or tactile assistance required"),
            QuestionOption(value="ID", label="Intellectual Disability (ID / Cognitive Support)", icon="🧠", description="Structured paced learning support"),
        ]


def get_mobility_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="village_block", label="🏡 अपने गाँव या ब्लॉक के अंदर (Within Village / Block)", icon="🏡"),
            QuestionOption(value="within_15km", label="🚲 15 किमी तक (नजदीकी कस्बा / बाजार)", icon="🚲"),
            QuestionOption(value="district_wide", label="🚌 अपने पूरे जिले में कहीं भी (District-wide)", icon="🚌"),
            QuestionOption(value="relocate_hostel", label="🎒 रहने (होस्टल) की सुविधा हो तो बाहर जाने को तैयार", icon="🎒"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="village_block", label="🏡 নিজের গ্রাম বা ব্লকের মধ্যে (Within Village / Block)", icon="🏡"),
            QuestionOption(value="within_15km", label="🚲 ১৫ কিমি পর্যন্ত (কাছের বাজার বা শহর)", icon="🚲"),
            QuestionOption(value="district_wide", label="🚌 জেলার যেকোনো জায়গায় (District-wide)", icon="🚌"),
            QuestionOption(value="relocate_hostel", label="🎒 হোস্টেল সুবিধা থাকলে অন্যত্র যেতে প্রস্তুত", icon="🎒"),
        ]
    else:
        return [
            QuestionOption(value="village_block", label="Within own village / block", icon="🏡"),
            QuestionOption(value="within_15km", label="Up to 15 km (Nearby market / town)", icon="🚲"),
            QuestionOption(value="district_wide", label="Anywhere across my district", icon="🚌"),
            QuestionOption(value="relocate_hostel", label="Willing to relocate if residential hostel provided", icon="🎒"),
        ]


def get_goal_options(lang: str = "hi") -> List[QuestionOption]:
    if lang == "hi":
        return [
            QuestionOption(value="training_stipend", label="📜 प्रमाणित सरकारी ट्रेनिंग + मासिक वजीफा (Stipend)", icon="📜"),
            QuestionOption(value="job_placement", label="💼 नजदीकी क्षेत्र में तुरंत पक्की नौकरी (Job Placement)", icon="💼"),
            QuestionOption(value="micro_business", label="🏪 अपनी खुद की दुकान या व्यवसाय शुरू करना (Self-employment)", icon="🏪"),
        ]
    elif lang == "bn":
        return [
            QuestionOption(value="training_stipend", label="📜 সরকারি সার্টিফিকেট প্রশিক্ষণ + মাসিক বৃত্তি (Stipend)", icon="📜"),
            QuestionOption(value="job_placement", label="💼 অবিলম্বে স্থানীয় চাকরির নিয়োগ (Job Placement)", icon="💼"),
            QuestionOption(value="micro_business", label="🏪 নিজের ছোট ব্যবসা বা উদ্যোগ শুরু করা (Self-employment)", icon="🏪"),
        ]
    else:
        return [
            QuestionOption(value="training_stipend", label="Certified Government Training + Monthly Stipend", icon="📜"),
            QuestionOption(value="job_placement", label="Immediate Local Job Placement", icon="💼"),
            QuestionOption(value="micro_business", label="Start My Own Micro-Business / Shop", icon="🏪"),
        ]
