from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List


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
# DATABASE SERVICE (INIT)
# =========================

class DatabaseService:
    @staticmethod
    def initialise():
        # Placeholder for future DB init
        return None


# =========================
# SFT SERVICE
# =========================

class SFTService:
    _submissions: List[SFTSubmission] = []
    _window: Optional[SFTWindow] = None

    # ---------- SFT WINDOW (IC CONTROL) ----------

    @classmethod
    def set_window(cls, date: str, start: str, end: str):
        cls._window = SFTWindow(date=date, start=start, end=end)

    @classmethod
    def get_window(cls) -> Optional[SFTWindow]:
        return cls._window

    @classmethod
    def clear_window(cls):
        cls._window = None

    # ---------- INTERNAL TIME HELPERS ----------

    @staticmethod
    def _to_minutes(t: str) -> int:
        return int(t[:2]) * 60 + int(t[2:])

    # ---------- SUBMISSION CONTROL ----------

    @classmethod
    def can_submit(cls) -> bool:
        return cls._window is not None

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

        # Convert to minutes
        w_start = cls._to_minutes(cls._window.start)
        w_end = cls._to_minutes(cls._window.end)
        s_start = cls._to_minutes(start)
        s_end = cls._to_minutes(end)

        # ---------- VALIDATION ----------

        # Time must be within window
        if not (w_start <= s_start < s_end <= w_end):
            raise ValueError("Selected time is outside SFT window")

        # One pax per activity
        for s in cls._submissions:
            if s.date == cls._window.date and s.activity == activity:
                raise ValueError(
                    f"Activity '{activity}' already has a participant"
                )

        # One submission per user (recommended)
        for s in cls._submissions:
            if s.date == cls._window.date and s.user_id == user_id:
                raise ValueError("You have already submitted SFT")

        # ---------- SAVE ----------

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

    # ---------- QUERYING ----------

    @classmethod
    def get_submissions_by_date(cls, date: str) -> List[SFTSubmission]:
        return [s for s in cls._submissions if s.date == date]

    @classmethod
    def generate_summary(cls, date: str) -> str:
        grouped = defaultdict(list)

        for submission in cls._submissions:
            if submission.date != date:
                continue
            key = f"{submission.activity} @ {submission.location}"
            grouped[key].append(submission)

        if not grouped:
            return f"No SFT submissions for {date}."

        lines = [f"SFT Summary ({date})"]

        for activity, entries in grouped.items():
            lines.append(f"\n{activity}:")
            for idx, entry in enumerate(entries, 1):
                lines.append(
                    f"{idx}. {entry.user_name} "
                    f"{entry.start}-{entry.end}"
                )

        return "\n".join(lines)
