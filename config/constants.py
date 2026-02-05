import os


def _int_env(key, default=0):
    value = os.getenv(key)
    if value is None or value == "":
        return default
    return int(value)


IC_GROUP_CHAT_ID = _int_env("IC_GROUP_CHAT_ID", 0)
SFT_TOPIC_ID = _int_env("SFT_TOPIC_ID", 0)
MOVEMENT_TOPIC_ID = _int_env("MOVEMENT_TOPIC_ID", 0)

LOCATIONS = [
    loc.strip()
    for loc in os.getenv("MOVEMENT_LOCATIONS", "HQ,Training Area,Mess").split(",")
    if loc.strip()
]

SFT_ACTIVITIES = []
for item in os.getenv("SFT_ACTIVITIES", "SFT @ Gym,PT @ Track").split(","):
    item = item.strip()
    if not item:
        continue
    if "@" in item:
        activity, location = [part.strip() for part in item.split("@", 1)]
        SFT_ACTIVITIES.append((activity, location))
    else:
        SFT_ACTIVITIES.append((item, "Gym"))

PERSONNEL_NAMES = [
    name.strip()
    for name in os.getenv("PERSONNEL_NAMES", "Personnel 1,Personnel 2").split(",")
    if name.strip()
]
