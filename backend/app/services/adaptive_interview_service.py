"""
Utthan Backend - Adaptive Beneficiary Interview & Structured Profile Engine.
Phase 3B: Catalog-Aware Adaptive Interview State Machine & NSQF Competency Evidence.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from supabase import Client

from app.schemas.adaptive_interview import (
    AdaptiveAnswerSubmit,
    AdaptiveInterviewState,
    AdaptiveQuestion,
    InputMethod,
    InterviewStage,
    NSQFCompetencyEvidence,
    QuestionInputType,
    QuestionOption,
    StructuredBeneficiaryProfile,
)
from app.schemas.beneficiary import LanguageCode
from app.services.interview_localization import (
    get_education_options,
    get_experience_options,
    get_goal_options,
    get_mobility_options,
    get_notional_hours_options,
    get_pwd_options,
    get_stage_title,
    get_vocational_options,
)
from app.services.nsqf_service import list_sectors, query_courses

logger = logging.getLogger("utthan.adaptive_interview")

STAGES_ORDER: List[InterviewStage] = [
    InterviewStage.LOCATION,
    InterviewStage.BASIC_PROFILE,
    InterviewStage.EDUCATION,
    InterviewStage.VOCATIONAL_TRAINING,
    InterviewStage.EXPERIENCE,
    InterviewStage.SECTOR,
    InterviewStage.CATALOG_CONTEXT,
    InterviewStage.COMPETENCY_EVIDENCE,
    InterviewStage.CAPACITY_HOURS,
    InterviewStage.PWD,
    InterviewStage.WORK_PREFERENCES,
    InterviewStage.REVIEW,
    InterviewStage.COMPLETED,
]

# Canonical sector keyword mapping for fast resolution
SECTOR_ICONS: Dict[str, str] = {
    "agriculture": "🌾",
    "it-ites": "💻",
    "electronics-hw": "⚡",
    "healthcare": "🩺",
    "automotive": "🚗",
    "apparel": "🧵",
    "handicrafts-carpets": "🧶",
    "construction": "🏗️",
    "beauty-wellness": "💄",
    "tourism-hospitality": "🏨",
    "plumbing": "🔧",
    "green-jobs": "🌱",
    "environmental-science": "♻️",
    "persons-with-disability": "♿",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _load_interview_row(client: Client, interview_id: UUID, beneficiary_id: UUID) -> Dict[str, Any]:
    """Loads interview row from Supabase or memory."""
    res = (
        client.table("interview_sessions")
        .select("*")
        .eq("id", str(interview_id))
        .eq("beneficiary_id", str(beneficiary_id))
        .limit(1)
        .execute()
    )
    rows = getattr(res, "data", [])
    if not rows:
        raise LookupError(f"Interview session {interview_id} not found for beneficiary {beneficiary_id}.")
    return rows[0]


def _load_beneficiary_row(client: Client, beneficiary_id: UUID) -> Dict[str, Any]:
    """Loads beneficiary row from Supabase or memory."""
    res = (
        client.table("beneficiaries")
        .select("*")
        .eq("id", str(beneficiary_id))
        .limit(1)
        .execute()
    )
    rows = getattr(res, "data", [])
    if not rows:
        raise LookupError(f"Beneficiary {beneficiary_id} not found.")
    return rows[0]


def get_or_initialize_profile(
    interview_row: Dict[str, Any],
    beneficiary_row: Dict[str, Any],
) -> StructuredBeneficiaryProfile:
    """Constructs StructuredBeneficiaryProfile from persisted extracted_profile or base tables."""
    extracted = interview_row.get("extracted_profile") or {}
    responses = interview_row.get("responses") or {}

    b_id = UUID(str(interview_row["beneficiary_id"]))
    i_id = UUID(str(interview_row["id"]))
    lang = interview_row.get("language") or beneficiary_row.get("preferred_language") or "hi"

    # Merge extracted with base tables for resilience
    state_id = extracted.get("state_id") or beneficiary_row.get("state_id")
    district_id = extracted.get("district_id") or beneficiary_row.get("district_id")
    name = extracted.get("name") or beneficiary_row.get("name")
    edu = extracted.get("education") or beneficiary_row.get("education_level") or "no_formal"
    mobility = extracted.get("mobility_preference") or beneficiary_row.get("mobility_preference") or "within_15km"
    goal = extracted.get("primary_goal") or beneficiary_row.get("primary_goal") or "training_stipend"

    competency_dict = extracted.get("competency_evidence") or {}
    competency_obj = NSQFCompetencyEvidence(
        professional_knowledge=competency_dict.get("professional_knowledge", []),
        technical_skills=competency_dict.get("technical_skills", []),
        core_skills=competency_dict.get("core_skills", []),
        process_capability=competency_dict.get("process_capability", []),
        responsibility_level=competency_dict.get("responsibility_level"),
    )

    profile = StructuredBeneficiaryProfile(
        beneficiary_id=b_id,
        interview_id=i_id,
        preferred_language=lang,
        name=name,
        state_id=state_id,
        state_name=extracted.get("state_name"),
        district_id=district_id,
        district_name=extracted.get("district_name"),
        education=edu,
        education_label=extracted.get("education_label"),
        previous_nsqf_qualification=extracted.get("previous_nsqf_qualification"),
        vocational_training=extracted.get("vocational_training", False),
        vocational_training_type=extracted.get("vocational_training_type"),
        work_experience_years=float(extracted.get("work_experience_years") or 0.0),
        work_experience_label=extracted.get("work_experience_label"),
        current_occupation=extracted.get("current_occupation") or beneficiary_row.get("current_occupation"),
        interested_sector_id=extracted.get("interested_sector_id"),
        interested_sector_name=extracted.get("interested_sector_name"),
        target_qualifications=extracted.get("target_qualifications", []),
        notional_hours_range=extracted.get("notional_hours_range"),
        pwd_status=extracted.get("pwd_status", False),
        pwd_categories=extracted.get("pwd_categories", []),
        pwd_checked=extracted.get("pwd_checked", False),
        skills=extracted.get("skills", []),
        competencies=extracted.get("competencies", []),
        tools_familiarity=extracted.get("tools_familiarity", []),
        competency_evidence=competency_obj,
        mobility_preference=mobility,
        primary_goal=goal,
        completeness_percentage=int(extracted.get("completeness_percentage") or 0),
        created_at=interview_row.get("created_at"),
        updated_at=interview_row.get("updated_at"),
    )
    return profile


def calculate_completeness(profile: StructuredBeneficiaryProfile) -> int:
    """Calculates weighted completeness percentage of the structured profile."""
    score = 0
    if profile.state_id and profile.district_id:
        score += 15
    if profile.name:
        score += 10
    if profile.education:
        score += 15
    if profile.interested_sector_id:
        score += 20
    if profile.work_experience_years is not None:
        score += 10
    if profile.target_qualifications or profile.skills:
        score += 15
    if profile.notional_hours_range:
        score += 5
    if profile.mobility_preference and profile.primary_goal:
        score += 10
    return min(100, score)


def determine_current_stage(profile: StructuredBeneficiaryProfile, status: str) -> Tuple[InterviewStage, int]:
    """Evaluates profile state to determine the active interview stage."""
    if status == "completed":
        return InterviewStage.COMPLETED, len(STAGES_ORDER) - 1

    if not profile.state_id or not profile.district_id:
        return InterviewStage.LOCATION, 0

    if not profile.name or profile.name.lower() in ("citizen", "anonymous", ""):
        return InterviewStage.BASIC_PROFILE, 1

    if not profile.education or profile.education == "no_formal" and not profile.education_label:
        return InterviewStage.EDUCATION, 2

    # Check vocational training
    if profile.vocational_training_type is None:
        return InterviewStage.VOCATIONAL_TRAINING, 3

    if profile.work_experience_label is None and profile.work_experience_years == 0.0:
        return InterviewStage.EXPERIENCE, 4

    if not profile.interested_sector_id:
        return InterviewStage.SECTOR, 5

    # Catalog-aware stage: pick job role in sector
    if not profile.target_qualifications:
        return InterviewStage.CATALOG_CONTEXT, 6

    # Competency evidence: tools / responsibility
    if not profile.tools_familiarity and not profile.competency_evidence.technical_skills:
        return InterviewStage.COMPETENCY_EVIDENCE, 7

    if not profile.notional_hours_range:
        return InterviewStage.CAPACITY_HOURS, 8

    if not profile.pwd_checked:
        return InterviewStage.PWD, 9

    if not profile.mobility_preference or not profile.primary_goal:
        return InterviewStage.WORK_PREFERENCES, 10

    return InterviewStage.REVIEW, 11


def generate_adaptive_question(
    stage: InterviewStage,
    profile: StructuredBeneficiaryProfile,
    lang: str = "hi",
    client: Optional[Client] = None,
) -> Optional[AdaptiveQuestion]:
    """
    Constructs the next deterministic, catalog-aware interview question based on stage and collected evidence.
    """
    title = get_stage_title(stage.value, lang)

    if stage == InterviewStage.LOCATION:
        q_text = {
            "hi": "कृपया अपने राज्य और जिले का चयन करें ताकि हम आपके नजदीकी केंद्र ढूंढ सकें।",
            "bn": "আপনার রাজ্য ও জেলা নির্বাচন করুন যাতে আমরা নিকটবর্তী কেন্দ্র খুঁজে পেতে পারি।",
            "en": "Please confirm your State and District to locate nearby certified training centers.",
        }.get(lang, "Please confirm your State and District.")

        return AdaptiveQuestion(
            question_id="loc_state_district",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.LOCATION_SELECT,
            field_target="state_id,district_id",
            reason="State and district determine jurisdictional scheme eligibility and local training centers.",
            help_text="Speak or select your native district.",
        )

    elif stage == InterviewStage.BASIC_PROFILE:
        q_text = {
            "hi": "आपका शुभ नाम क्या है? (आप बोलकर या लिखकर बता सकते हैं)",
            "bn": "আপনার নাম কী? (আপনি মুখে বলতে পারেন বা টাইপ করতে পারেন)",
            "en": "What is your full name? (You can speak or type your name)",
        }.get(lang, "What is your full name?")

        return AdaptiveQuestion(
            question_id="bio_name",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.VOICE_TEXT,
            field_target="name",
            reason="Captures the beneficiary's name for digital profile enrollment.",
            help_text="Speak your name clearly into the microphone.",
        )

    elif stage == InterviewStage.EDUCATION:
        q_text = {
            "hi": "आपकी उच्चतम शैक्षणिक योग्यता (Highest Education) क्या है?",
            "bn": "আপনার সর্বোচ্চ শিক্ষাগত যোগ্যতা কত দূর?",
            "en": "What is your highest level of formal or informal schooling?",
        }.get(lang, "What is your highest level of schooling?")

        return AdaptiveQuestion(
            question_id="edu_highest_level",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=get_education_options(lang),
            field_target="education",
            reason="Matches prerequisite educational criteria for NSQF courses and PM-AJAY schemes.",
            help_text="Select or speak your highest schooling level.",
        )

    elif stage == InterviewStage.VOCATIONAL_TRAINING:
        q_text = {
            "hi": "क्या आपने पहले कोई आईटीआई (ITI), सीटीएस, या सरकारी कौशल प्रशिक्षण प्राप्त किया है?",
            "bn": "আপনি কি পূর্বে কোনো আইটিআই (ITI), ভোকেশনাল বা সরকারি স্কিল ট্রেনিং নিয়েছেন?",
            "en": "Have you completed any formal ITI, vocational certificate, or apprenticeship training?",
        }.get(lang, "Have you completed any vocational or ITI training?")

        return AdaptiveQuestion(
            question_id="voc_training_type",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=get_vocational_options(lang),
            field_target="vocational_training_type",
            reason="Identifies eligibility for lateral entry into higher NSQF levels (e.g. Level 4+).",
        )

    elif stage == InterviewStage.EXPERIENCE:
        q_text = {
            "hi": "आपको व्यावहारिक काम या मजदूरी/कारीगरी का कितने समय का अनुभव है?",
            "bn": "আপনার ব্যবহারিক কাজের বা কারিগরি ক্ষেত্রে কতদিনের কাজের অভিজ্ঞতা আছে?",
            "en": "How many years of practical work experience do you have in any livelihood trade?",
        }.get(lang, "How many years of work experience do you have?")

        return AdaptiveQuestion(
            question_id="exp_years",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=get_experience_options(lang),
            field_target="work_experience_years",
            reason="Captures experiential baseline to support Recognition of Prior Learning (RPL).",
        )

    elif stage == InterviewStage.SECTOR:
        # Load active sectors dynamically from nsqf_service
        sectors = list_sectors(client=client)
        options = []
        for s in sectors[:12]:  # Show top 12 active sectors
            icon = SECTOR_ICONS.get(s.id, "🏭")
            options.append(QuestionOption(value=s.id, label=f"{s.name} ({s.course_count} courses)", icon=icon))

        q_text = {
            "hi": "आप किस उद्योग या काम के क्षेत्र में नया कौशल सीखना या आगे बढ़ना चाहते हैं?",
            "bn": "আপনি কোন শিল্প বা কাজের ক্ষেত্রে নতুন দক্ষতা শিখতে বা এগিয়ে যেতে চান?",
            "en": "Which industry sector are you most interested in training for?",
        }.get(lang, "Which industry sector are you most interested in?")

        return AdaptiveQuestion(
            question_id="sec_interested_sector",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=options,
            field_target="interested_sector_id",
            reason="Filters the 2,810 course catalog down to the beneficiary's target trade sector.",
            help_text="Select your preferred industry sector.",
        )

    elif stage == InterviewStage.CATALOG_CONTEXT:
        # CATALOG-AWARE: Query real qualifications from the chosen sector!
        sector_id = profile.interested_sector_id or "agriculture"
        catalog_res = query_courses(client=client, sector_id=sector_id, page=1, page_size=6)
        
        options = []
        for q in catalog_res.items:
            label = f"{q.title} (Level {q.nsqf_level})"
            options.append(QuestionOption(
                value=q.q_code,
                label=label,
                icon="🎯",
                description=f"NQR Code: {q.q_code} | {q.notional_hours_range or 'Standard'} hours"
            ))

        # Add a general option
        options.append(QuestionOption(value="general_sector_all", label="इस क्षेत्र के सभी उपयुक्त कोर्स (All courses in this sector)", icon="✨"))

        q_text = {
            "hi": f"{profile.interested_sector_name or 'इस क्षेत्र'} में आधिकारिक NQR के ये कोर्स उपलब्ध हैं। आप किस काम में विशेष रुचि रखते हैं?",
            "bn": f"{profile.interested_sector_name or 'এই ক্ষেত্রে'} সরকারি NQR নিবন্ধিত এই কোর্সগুলো রয়েছে। আপনি কোনটিতে আগ্রহী?",
            "en": f"The authoritative NQR catalog offers these qualifications in {profile.interested_sector_name or 'this sector'}. Which specific role interests you?",
        }.get(lang, "Which specific qualification or role in this sector interests you?")

        return AdaptiveQuestion(
            question_id="cat_target_qualifications",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=options,
            field_target="target_qualifications",
            catalog_context={"sector_id": sector_id, "sample_courses_count": len(catalog_res.items)},
            reason="Grounds the interview directly in official NSQF qualifications from the chosen sector.",
            help_text="Choose the role that aligns closest with your livelihood ambitions.",
        )

    elif stage == InterviewStage.COMPETENCY_EVIDENCE:
        # NSQF Dimension evidence: tools and responsibility
        sec_id = profile.interested_sector_id or "agriculture"
        tool_options_map = {
            "agriculture": [
                QuestionOption(value="drip_sprayers", label="ड्रिप सिंचाई एवं छिड़काव पंप (Sprayers / Irrigation)", icon="🚿"),
                QuestionOption(value="tractor_tiller", label="ट्रैक्टर एवं पावर टिलर (Tractor / Tiller)", icon="🚜"),
                QuestionOption(value="drone_agritech", label="किषान ड्रोन एवं डिजिटल सेंसर (Drones / Sensors)", icon="🛰️"),
                QuestionOption(value="traditional_tools", label="पारंपरिक कृषि औजार (कल्टीवेटर, खुरपी, हसिया)", icon="🌾"),
            ],
            "it-ites": [
                QuestionOption(value="computer_office", label="कंप्यूटर एवं एमएस ऑफिस / टाइपिंग (Computer / Office)", icon="⌨️"),
                QuestionOption(value="smartphone_internet", label="स्मार्टफोन ऐप्स एवं इंटरनेट ब्राउजिंग (Smartphone / Web)", icon="📱"),
                QuestionOption(value="hardware_cables", label="कंप्यूटर हार्डवेयर एवं नेटवर्किंग केबल (Hardware / Cables)", icon="🖥️"),
                QuestionOption(value="data_entry", label="डाटा एंट्री एवं फाइल मैनेजमेंट (Data Entry)", icon="📄"),
            ],
            "electronics-hw": [
                QuestionOption(value="multimeter_tester", label="मल्टीमीटर एवं टेस्टर (Multimeter / Tester)", icon="⚡"),
                QuestionOption(value="soldering_iron", label="सोल्डरिंग आयरन एवं वायर स्ट्रिपर (Soldering Iron)", icon="🔌"),
                QuestionOption(value="home_appliances", label="घरेलू उपकरण (पंखा, कूलर, एसी मरम्मत)", icon="❄️"),
            ],
            "healthcare": [
                QuestionOption(value="first_aid_kit", label="प्राथमिक चिकित्सा किट (First Aid Kit)", icon="🩹"),
                QuestionOption(value="bp_sugar_meters", label="बीपी एवं शुगर जांच मशीन (BP & Glucose Meters)", icon="🩺"),
                QuestionOption(value="patient_care", label="मरीज की देखभाल एवं स्वच्छता (Patient Handling)", icon="🛏️"),
            ],
            "automotive": [
                QuestionOption(value="hand_tools", label="पाना, रिंच एवं स्क्रूड्राइवर सेट (Spanners & Wrenches)", icon="🔧"),
                QuestionOption(value="two_wheeler", label="बाइक / स्कूटर सर्विसिंग (Two-Wheeler Repair)", icon="🛵"),
                QuestionOption(value="car_driving", label="चार पहिया वाहन ड्राइविंग (Driving License)", icon="🚙"),
            ]
        }
        options = tool_options_map.get(sec_id, [
            QuestionOption(value="hand_tools", label="हस्त औजार एवं बुनियादी उपकरण (Basic Hand Tools)", icon="🔨"),
            QuestionOption(value="power_equipment", label="इलेक्ट्रिक उपकरण / मशीन (Power Equipment)", icon="⚙️"),
            QuestionOption(value="measuring_tools", label="मापक टेप एवं गेज (Measuring Tools)", icon="📐"),
            QuestionOption(value="safety_gear", label="सुरक्षा उपकरण (PPE Kit / Helmet / Gloves)", icon="🦺"),
        ])

        q_text = {
            "hi": "इस काम से जुड़े किन औजारों या उपकरणों को आप पहले इस्तेमाल कर चुके हैं या चलाना चाहते हैं?",
            "bn": "এই কাজের সাথে সম্পর্কিত কোন যন্ত্রপাতি বা সরঞ্জাম আপনি আগে ব্যবহার করেছেন বা চালাতে চান?",
            "en": "Which tools, equipment, or machinery have you previously handled or wish to learn?",
        }.get(lang, "Which tools or equipment have you handled?")

        return AdaptiveQuestion(
            question_id="comp_tools_familiarity",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.MULTI_CHOICE,
            options=options,
            field_target="tools_familiarity",
            reason="Captures concrete NSQF Technical Skills & Process Capability descriptor evidence.",
            help_text="You can select more than one option.",
        )

    elif stage == InterviewStage.CAPACITY_HOURS:
        q_text = {
            "hi": "आप प्रतिदिन या कुल कितने समय का प्रशिक्षण (Training Duration) आसानी से ले सकते हैं?",
            "bn": "আপনি কতদিনের বা কত ঘণ্টার প্রশিক্ষণ সহজে সম্পন্ন করতে পারবেন?",
            "en": "What notional training duration best fits your current availability?",
        }.get(lang, "What training duration fits your availability?")

        return AdaptiveQuestion(
            question_id="cap_notional_hours",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=get_notional_hours_options(lang),
            field_target="notional_hours_range",
            reason="Matches the NQR notional training hours range (1-200, 201-400, 401-600, etc.).",
        )

    elif stage == InterviewStage.PWD:
        q_text = {
            "hi": "क्या आप दिव्यांगजन (PwD) श्रेणी में आते हैं अथवा आपको किसी विशेष सुलभता सुविधा की आवश्यकता है?",
            "bn": "আপনি কি বিশেষ চাহিদাসম্পন্ন (PwD) ব্যক্তি বা আপনার কোনো বিশেষ সহায়তার প্রয়োজন আছে?",
            "en": "Do you identify as a Person with Disability (PwD) or require specialized accessibility support?",
        }.get(lang, "Do you identify as a Person with Disability?")

        return AdaptiveQuestion(
            question_id="pwd_status_category",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=get_pwd_options(lang),
            field_target="pwd_status",
            reason="Ensures dedicated SCPwD specialized courses (233 courses) and accommodations are identified.",
            help_text="Select your category or choose General/No Disability.",
        )

    elif stage == InterviewStage.WORK_PREFERENCES:
        q_text = {
            "hi": "आप दैनिक काम या ट्रेनिंग के लिए कितनी दूरी तक यात्रा कर सकते हैं?",
            "bn": "কাজের বা প্রশিক্ষণের জন্য আপনি প্রতিদিন কতটা দূরত্ব যাতায়াত করতে পারবেন?",
            "en": "How far are you comfortable commuting daily for skilling or employment?",
        }.get(lang, "How far are you comfortable commuting?")

        return AdaptiveQuestion(
            question_id="pref_mobility",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.SINGLE_CHOICE,
            options=get_mobility_options(lang),
            field_target="mobility_preference",
            reason="Determines whether local village center, district headquarters, or residential hostel is required.",
        )

    elif stage == InterviewStage.REVIEW:
        q_text = {
            "hi": "आपकी आजीविका प्रोफाइल तैयार है! कृपया नीचे दी गई जानकारी की पुष्टि करें या कोई बदलाव करें।",
            "bn": "আপনার জীবিকা প্রোফাইল তৈরি হয়েছে! অনুগ্রহ করে নিচের তথ্যগুলো যাচাই করুন বা সংশোধন করুন।",
            "en": "Your structured livelihood profile is ready! Please review the summary below before final submission.",
        }.get(lang, "Please review your structured profile before submitting.")

        return AdaptiveQuestion(
            question_id="rev_profile_confirmation",
            stage=stage,
            title=title,
            question_text=q_text,
            input_type=QuestionInputType.YES_NO,
            options=[
                QuestionOption(value="confirm", label="हाँ, सब सही है — सबमिट करें (Confirm & Submit)", icon="✅"),
                QuestionOption(value="edit", label="मुझे कुछ जानकारी बदलनी है (Edit Profile)", icon="✏️"),
            ],
            field_target="profile_confirmation",
            reason="Citizen verification gate guaranteeing explicit informed consent before lock-in.",
        )

    return None


def get_adaptive_interview_state(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
) -> AdaptiveInterviewState:
    """Retrieves full interview state, active question, and profile summary."""
    i_row = _load_interview_row(client, interview_id, beneficiary_id)
    b_row = _load_beneficiary_row(client, beneficiary_id)
    lang = i_row.get("language") or b_row.get("preferred_language") or "hi"

    profile = get_or_initialize_profile(i_row, b_row)
    profile.completeness_percentage = calculate_completeness(profile)

    stage, stage_idx = determine_current_stage(profile, i_row.get("status", "draft"))
    is_completed = i_row.get("status") == "completed"

    next_q = None
    if not is_completed:
        next_q = generate_adaptive_question(stage, profile, lang=lang, client=client)

    responses_dict = i_row.get("responses") or {}

    return AdaptiveInterviewState(
        interview_id=interview_id,
        beneficiary_id=beneficiary_id,
        language=lang,
        current_stage=stage,
        stage_index=stage_idx,
        total_stages=len(STAGES_ORDER) - 1,
        current_question=next_q,
        answered_questions_count=len(responses_dict),
        completeness_percentage=profile.completeness_percentage,
        can_go_back=stage_idx > 0,
        is_completed=is_completed,
        profile_summary=profile,
    )


def submit_answer_to_interview(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
    answer: AdaptiveAnswerSubmit,
) -> AdaptiveInterviewState:
    """
    Submits an answer, updates extracted_profile, syncs legacy response keys for recommendation engine,
    and returns updated state.
    """
    i_row = _load_interview_row(client, interview_id, beneficiary_id)
    b_row = _load_beneficiary_row(client, beneficiary_id)
    lang = answer.language or i_row.get("language") or "hi"

    if i_row.get("status") == "completed":
        raise ValueError("Cannot submit answers to an already completed interview.")

    profile = get_or_initialize_profile(i_row, b_row)
    extracted = profile.model_dump(exclude_none=True)
    responses = dict(i_row.get("responses") or {})

    # Map question_id to profile attributes
    q_id = answer.question_id
    val = answer.normalized_answer

    if q_id == "bio_name":
        profile.name = str(val).strip()
        extracted["name"] = profile.name

    elif q_id == "loc_state_district":
        if isinstance(val, dict):
            profile.state_id = val.get("state_id")
            profile.district_id = val.get("district_id")
            extracted["state_id"] = profile.state_id
            extracted["district_id"] = profile.district_id

    elif q_id == "edu_highest_level":
        profile.education = str(val).strip()
        profile.education_label = answer.raw_answer
        extracted["education"] = profile.education
        extracted["education_label"] = profile.education_label
        # Map to legacy responses key for backward compatibility with recommendation engine
        responses["education"] = answer.raw_answer

    elif q_id == "voc_training_type":
        profile.vocational_training_type = str(val).strip()
        profile.vocational_training = val != "none"
        extracted["vocational_training_type"] = profile.vocational_training_type
        extracted["vocational_training"] = profile.vocational_training

    elif q_id == "exp_years":
        try:
            profile.work_experience_years = float(val)
        except Exception:
            profile.work_experience_years = 0.0
        profile.work_experience_label = answer.raw_answer
        extracted["work_experience_years"] = profile.work_experience_years
        extracted["work_experience_label"] = profile.work_experience_label

    elif q_id == "sec_interested_sector":
        profile.interested_sector_id = str(val).strip()
        profile.interested_sector_name = answer.raw_answer
        extracted["interested_sector_id"] = profile.interested_sector_id
        extracted["interested_sector_name"] = profile.interested_sector_name
        # Map to legacy response key
        responses["workInterest"] = answer.raw_answer

    elif q_id == "cat_target_qualifications":
        if isinstance(val, list):
            profile.target_qualifications = [str(x).strip() for x in val]
        elif val != "general_sector_all":
            profile.target_qualifications = [str(val).strip()]
        else:
            profile.target_qualifications = [profile.interested_sector_id or "general"]
        extracted["target_qualifications"] = profile.target_qualifications

    elif q_id == "comp_tools_familiarity":
        tools_list = val if isinstance(val, list) else [str(val)]
        profile.tools_familiarity = tools_list
        profile.competency_evidence.technical_skills = tools_list
        extracted["tools_familiarity"] = tools_list
        extracted["competency_evidence"] = profile.competency_evidence.model_dump()

    elif q_id == "cap_notional_hours":
        profile.notional_hours_range = str(val).strip()
        extracted["notional_hours_range"] = profile.notional_hours_range

    elif q_id == "pwd_status_category":
        profile.pwd_checked = True
        extracted["pwd_checked"] = True
        is_pwd = val not in ("none", "pwd_none", False, "false", "no")
        profile.pwd_status = is_pwd
        if is_pwd:
            cat_clean = str(val).replace("pwd_", "").upper()
            profile.pwd_categories = [cat_clean] if cat_clean in ("VI", "SHI", "LD", "ID") else [str(val).strip()]
        else:
            profile.pwd_categories = []
        extracted["pwd_status"] = profile.pwd_status
        extracted["pwd_categories"] = profile.pwd_categories

    elif q_id == "pref_mobility":
        profile.mobility_preference = str(val).strip()
        extracted["mobility_preference"] = profile.mobility_preference
        responses["mobility"] = answer.raw_answer
        # Default goal if not set
        if not profile.primary_goal:
            profile.primary_goal = "training_stipend"
            responses["preference"] = "📜 Certified Training + Monthly Stipend"

    elif q_id == "rev_profile_confirmation":
        if str(val).strip() == "confirm":
            return complete_adaptive_session(client, interview_id, beneficiary_id)

    # Store answer audit log
    answer_log = extracted.setdefault("answer_log", [])
    answer_log.append({
        "question_id": q_id,
        "raw_answer": answer.raw_answer,
        "normalized_answer": answer.normalized_answer,
        "input_method": answer.input_method.value,
        "timestamp": _now().isoformat(),
    })

    # Update completeness
    profile.completeness_percentage = calculate_completeness(profile)
    extracted["completeness_percentage"] = profile.completeness_percentage

    # Save to interview_sessions
    new_rev = int(i_row.get("revision") or 1) + 1
    client.table("interview_sessions").update({
        "responses": responses,
        "extracted_profile": extracted,
        "revision": new_rev,
        "updated_at": _now().isoformat(),
    }).eq("id", str(interview_id)).execute()

    # Sync primary fields to beneficiaries table
    b_updates: Dict[str, Any] = {"updated_at": _now().isoformat()}
    if profile.name:
        b_updates["name"] = profile.name
    if profile.education:
        b_updates["education_level"] = profile.education
    if profile.mobility_preference:
        b_updates["mobility_preference"] = profile.mobility_preference
    if profile.primary_goal:
        b_updates["primary_goal"] = profile.primary_goal
    if profile.interested_sector_name:
        b_updates["current_occupation"] = profile.interested_sector_name
    if profile.state_id:
        b_updates["state_id"] = profile.state_id
    if profile.district_id:
        b_updates["district_id"] = profile.district_id

    client.table("beneficiaries").update(b_updates).eq("id", str(beneficiary_id)).execute()

    return get_adaptive_interview_state(client, interview_id, beneficiary_id)


def update_profile_field(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
    field_name: str,
    value: Any,
) -> StructuredBeneficiaryProfile:
    """Allows direct correction of a structured field during the review stage."""
    i_row = _load_interview_row(client, interview_id, beneficiary_id)
    b_row = _load_beneficiary_row(client, beneficiary_id)

    profile = get_or_initialize_profile(i_row, b_row)
    extracted = profile.model_dump(exclude_none=True)
    responses = dict(i_row.get("responses") or {})

    if hasattr(profile, field_name):
        setattr(profile, field_name, value)
        extracted[field_name] = value

    # If updating education or mobility, sync legacy keys
    if field_name == "education":
        responses["education"] = str(value)
    elif field_name == "mobility_preference":
        responses["mobility"] = str(value)
    elif field_name == "primary_goal":
        responses["preference"] = str(value)

    new_rev = int(i_row.get("revision") or 1) + 1
    client.table("interview_sessions").update({
        "responses": responses,
        "extracted_profile": extracted,
        "revision": new_rev,
        "updated_at": _now().isoformat(),
    }).eq("id", str(interview_id)).execute()

    # Sync to beneficiaries
    if field_name in ("name", "education_level", "mobility_preference", "primary_goal", "state_id", "district_id"):
        client.table("beneficiaries").update({
            field_name: value,
            "updated_at": _now().isoformat(),
        }).eq("id", str(beneficiary_id)).execute()

    return profile


def complete_adaptive_session(
    client: Client,
    interview_id: UUID,
    beneficiary_id: UUID,
) -> AdaptiveInterviewState:
    """Finalizes and locks the interview session as completed."""
    i_row = _load_interview_row(client, interview_id, beneficiary_id)
    b_row = _load_beneficiary_row(client, beneficiary_id)

    profile = get_or_initialize_profile(i_row, b_row)
    extracted = profile.model_dump(exclude_none=True)
    responses = dict(i_row.get("responses") or {})

    # Ensure all legacy keys exist for 100% backward compatibility
    if not responses.get("workInterest"):
        responses["workInterest"] = profile.interested_sector_name or "☀️ Solar & Electrical Maintenance"
    if not responses.get("education"):
        responses["education"] = profile.education_label or "🎓 10th Pass"
    if not responses.get("mobility"):
        responses["mobility"] = "🚲 Up to 15 km (Nearby Market / Town)"
    if not responses.get("preference"):
        responses["preference"] = "📜 Certified Training + Monthly Stipend"

    now_iso = _now().isoformat()
    new_rev = int(i_row.get("revision") or 1) + 1

    client.table("interview_sessions").update({
        "status": "completed",
        "responses": responses,
        "extracted_profile": extracted,
        "completed_at": now_iso,
        "revision": new_rev,
        "updated_at": now_iso,
    }).eq("id", str(interview_id)).execute()

    return get_adaptive_interview_state(client, interview_id, beneficiary_id)
