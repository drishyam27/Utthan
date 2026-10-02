"""Typed interview lifecycle contracts for Phase 2C."""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.beneficiary import LanguageCode


InterviewStatus = Literal["draft", "completed"]


INTERVIEW_RESPONSE_OPTIONS = {
    "workInterest": frozenset(
        {
            "☀️ Solar & Electrical Maintenance",
            "🧵 Tailoring & Handloom Weaving",
            "🌾 Agri-Tech & Drone Farming",
            "🩺 Healthcare Assistant (GDA)",
            "🚗 Driving & Auto Mechanics",
            "☀️ सोलर एवं इलेक्ट्रीशियन",
            "🧵 सिलाई एवं हथकरघा बुनाई",
            "🌾 आधुनिक कृषि एवं ड्रोन पायलट",
            "🩺 स्वास्थ्य सहायक (GDA)",
            "🚗 ड्राइविंग एवं मोटर मैकेनिक",
            "☀️ সোলার প্যানেল ও ইলেকট্রিশিয়ান",
            "🧵 সেলাই ও তাঁতশিল্প",
            "🌾 আধুনিক কৃষি ও কিষাণ ড্রোন",
            "🩺 স্বাস্থ্য সহকারী (GDA)",
            "🚗 ড্রাইভিং ও অটোমোবাইল মেকানিক",
        }
    ),
    "education": frozenset(
        {
            "🎓 10th Pass",
            "📚 12th Pass",
            "🏫 8th Pass or Below",
            "🛠️ ITI / Vocational Diploma",
            "🌱 No formal schooling (Eager to learn)",
            "🎓 10वीं पास",
            "📚 12वीं पास",
            "🏫 8वीं पास या उससे कम",
            "🛠️ आईटीआई / वोकेशनल डिप्लोमा",
            "🌱 अनौपचारिक शिक्षा (सीखने के इच्छुक)",
            "🎓 ১০ম শ্রেণী (মাধ্যমিক) পাস",
            "📚 ১২ম শ্রেণী (উচ্চমাধ্যমিক) পাস",
            "🏫 ৮ম শ্রেণী বা তার নিচে",
            "🛠️ আইটিআই বা ভোকেশনাল ডিপ্লোমা",
            "🌱 প্রাতিষ্ঠানিক পড়াশোনা নেই (শিখতে আগ্রহী)",
        }
    ),
    "mobility": frozenset(
        {
            "🏡 Within my own village / block",
            "🚲 Up to 15 km (Nearby Market / Town)",
            "🚌 Anywhere in my district",
            "🎒 Willing to relocate if hostel provided",
            "🏡 अपने गाँव या ब्लॉक के अंदर",
            "🚲 15 किमी तक (नजदीकी कस्बा)",
            "🚌 अपने पूरे जिले में कहीं भी",
            "🎒 रहने की सुविधा हो तो बाहर जाने को तैयार",
            "🏡 নিজের গ্রাম বা ব্লকের মধ্যে",
            "🚲 ১৫ কিমি পর্যন্ত (কাছের শহর)",
            "🚌 জেলার যেকোনো জায়গায়",
            "🎒 হোস্টেল ও থাকার ব্যবস্থা থাকলে বাইরে যেতে প্রস্তুত",
        }
    ),
    "preference": frozenset(
        {
            "📜 Certified Training + Monthly Stipend",
            "💼 Immediate Local Job Placement",
            "🏪 Start My Own Micro-Business / Shop",
            "📜 प्रमाणित सरकारी ट्रेनिंग + मासिक वजीफा",
            "💼 नजदीकी क्षेत्र में तुरंत पक्की नौकरी",
            "🏪 अपनी खुद की दुकान या व्यवसाय शुरू करना",
            "📜 সার্টিফিকেট প্রশিক্ষণ + মাসিক বৃত্তি (Stipend)",
            "💼 এলাকায় দ্রুত চাকরির সুযোগ",
            "🏪 নিজের ছোট দোকান বা স্বনির্ভর ব্যবসা শুরু করা",
        }
    ),
}


class InterviewResponsesContract(BaseModel):
    """The exact four response keys and option values used by ConversationPage."""

    model_config = ConfigDict(extra="forbid")

    workInterest: Optional[str] = None
    education: Optional[str] = None
    mobility: Optional[str] = None
    preference: Optional[str] = None

    @field_validator("workInterest", "education", "mobility", "preference")
    @classmethod
    def validate_answer_option(cls, value: Optional[str], info):
        if value is not None and value not in INTERVIEW_RESPONSE_OPTIONS[info.field_name]:
            raise ValueError(f"unsupported answer for {info.field_name}")
        return value

    def required_fields_present(self) -> bool:
        return all(
            getattr(self, field_name) is not None
            for field_name in INTERVIEW_RESPONSE_OPTIONS
        )


class InterviewCreateRequest(BaseModel):
    """Creation/resume request; beneficiary ownership comes from the capability."""

    model_config = ConfigDict(extra="forbid")

    language: LanguageCode = "hi"


class InterviewDraftUpdateRequest(BaseModel):
    """Whole-response draft update with optimistic concurrency."""

    model_config = ConfigDict(extra="forbid")

    responses: InterviewResponsesContract
    expected_revision: int = Field(..., ge=1)


class InterviewCompletionRequest(BaseModel):
    """Completion request guarded by the caller's last observed revision."""

    model_config = ConfigDict(extra="forbid")

    expected_revision: int = Field(..., ge=1)


class InterviewSessionContract(BaseModel):
    """Structured interview state; individual answers remain JSON data."""

    id: Optional[UUID] = None
    beneficiary_id: Optional[UUID] = None
    language: LanguageCode = "hi"
    status: InterviewStatus = "draft"
    responses: dict[str, Any] = Field(default_factory=dict)
    extracted_profile: Optional[dict[str, Any]] = None
    transcript_log: Optional[str] = None
    revision: int = Field(1, ge=1)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_completion_timestamp(self):
        if self.status == "completed" and self.completed_at is None:
            raise ValueError("completed interview sessions require completed_at")
        if self.status == "draft" and self.completed_at is not None:
            raise ValueError("draft interview sessions cannot have completed_at")
        return self
