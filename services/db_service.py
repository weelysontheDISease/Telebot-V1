from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional


# =========================
# DATA MODELS
# =========================

@dataclass
class SFTSubmission:
    user_id: int
    user_name: str
    activity: str
    location: str
    start: str
    end: str
    date: str


@dataclass
class SFTWindow:
    date: str
    start: str
    end: str


# =========================
# DATABASE SERVICE
# =========================

class DatabaseService:
    @staticmethod
    def initialise():
        return None


# =========================
# SFT SERVICE
# =========================

class SFTService:
    _submissions: List[SFTSubmission] = []
    _window: Optional[SFTWindow] = None

    # ---------- WINDOW CONTROL ----------

    @classmethod
    def set_window(cls, date: str, start: str, end: str):
        cls._window = SFTWindow(date=date, start=start, end=end)

    @classmethod
    def get_window(cls) -> Optional[SFTWindow]:
        return cls._window

    @classmethod
    def clear_window(cls):
        cls._window = None

    # ---------- SUBMISSIONS ----------

    @classmethod
    def add_submission(
        cls,
        user_id: int,
        activity: str,
        location: str,
        start: str,
        end: str,
        user_name: str,
    ):
        if not cls._window:
            raise ValueError("SFT window not set")

        cls._submissions.append(
            SFTSubmission(
                user_id=user_id,
                user_name=user_name,
                activity=activity,
                location=location,
                start=start,
                end=end,
                date=cls._window.date,
            )
        )

    @classmethod
    def remove_submission(cls, user_id: int):
        cls._submissions = [
            s for s in cls._submissions if s.user_id != user_id
        ]

    # ---------- SUMMARY GENERATION ----------

    @classmethod
    def generate_summary(cls, date: str) -> str:
        grouped = defaultdict(list)

        for s in cls._submissions:
            if s.date != date:
                continue
            key = f"{s.activity} @ {s.location}"
            grouped[key].append(s)

        if not grouped:
            return f"❌ No SFT submissions for {date}."

        # 🚨 VALIDATION: each activity must have >= 2 pax
        invalid = [
            activity
            for activity, entries in grouped.items()
            if len(entries) < 2
        ]

        if invalid:
            lines = [
                "❌ SFT summary cannot be generated.",
                "",
                "The following activities have fewer than 2 participants:",
            ]
            for a in invalid:
                lines.append(f"- {a}")
            lines.append("")
            lines.append("Please resolve before generating summary.")
            return "\n".join(lines)

        # ✅ VALID → build summary
        lines = [f"SFT Summary ({date})"]

        for activity, entries in grouped.items():
            lines.append(f"\n{activity}:")
            for idx, e in enumerate(entries, 1):
                lines.append(
                    f"{idx}. {e.user_name} {e.start}-{e.end}"
                )

        return "\n".join(lines)


# =========================
# FUNCTIONAL EXPORT
# =========================

def get_sft_window():
    return SFTService.get_window()

def set_sft_window(date: str, start: str, end: str):
    SFTService.set_window(date=date, start=start, end=end)