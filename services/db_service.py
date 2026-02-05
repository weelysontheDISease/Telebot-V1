from collections import defaultdict
from dataclasses import dataclass


@dataclass
class SFTSubmission:
    user_id: int
    user_name: str
    activity: str
    location: str
    start: str
    end: str
    date: str


class DatabaseService:
    @staticmethod
    def initialise():
        return None


class SFTService:
    _submissions = []

    @classmethod
    def add_submission(cls, user_id, activity, location, start, end, date, user_name=None):
        cls._submissions.append(
            SFTSubmission(
                user_id=user_id,
                user_name=user_name or f"User {user_id}",
                activity=activity,
                location=location,
                start=start,
                end=end,
                date=date,
            )
        )

    @classmethod
    def generate_summary(cls, date):
        grouped = defaultdict(list)
        for submission in cls._submissions:
            if submission.date != date:
                continue
            grouped[submission.activity].append(submission)

        if not grouped:
            return f"No SFT submissions for {date}."

        lines = [f"SFT Summary ({date})"]
        for activity, entries in grouped.items():
            lines.append(f"\n{activity}:")
            for idx, entry in enumerate(entries, 1):
                lines.append(
                    f"{idx}. {entry.user_name} @ {entry.location} "
                    f"{entry.start}-{entry.end}"
                )
        return "\n".join(lines)
