# =========================
# CHAT & TOPIC IDS
# =========================

# Instructors / IC Group (shared)
IC_GROUP_CHAT_ID = -1003592356953

# Topics in IC Group
MOVEMENT_TOPIC_ID = 322
SFT_TOPIC_ID = 7
PARADE_STATE_TOPIC_ID = 3
CET_TOPIC_ID = 2

# =========================
# CADET CHAT (CET)
# =========================

CADET_CHAT_ID = -1003675767444
CADET_CET_TOPIC_ID = 5


# =========================
# MOVEMENT CONFIG
# =========================

LOCATIONS = [
    "DHA",
    "WINGLINE",
    "THROW TRASH",
    "OCS HQ",
    "STADIUM",
    "MEDICAL CENTRE",
    "AUDITORIUM",
    "EXAM HALL",
    "E-MART",
    "LIBRARY"
]

# =========================
# SFT CONFIG
# =========================

ACTIVITIES = [
    "Gym @ Wingline",
    "Running @ Yellow Cluster Parade Square",
    "Running @ DIS Wing Approved Route",
    "Frisbee @ Basketball court",
    "Basketball @ Basketball court",
    "Other ball @ Yellow Cluster Parade Square",
    "Badminton @ Basketball court"
]


# =========================
# PARADE STATE CONFIG
# =========================

# Order in which parade state sections appear
PARADE_STATE_SECTION_ORDER = [
    "MA",
    "RSI",
    "RSO",
    "MC",
    "OTHERS",
    "STATUSES",
    "PERMANENT_STATUS"
]

# Display names for each section
PARADE_STATE_SECTION_TITLES = {
    "MA": "MA",
    "RSI": "RSI",
    "RSO": "RSO",
    "MC": "MC",
    "OTHERS": "OTHERS",
    "STATUSES": "STATUSES",
    "PERMANENT_STATUS": "PERMANENT STATUS"
}

PARADE_STATE_FIELDS = {
    "MA": [
        ("appointment_type", "NAME"),
        ("location", "LOCATION"),
        ("date", "DATE"),
        ("time", "TIME OF APPOINTMENT"),
    ],


    "RSI": [
        ("symptoms", "SYMPTOMS"),
        ("diagnosis", "DIAGNOSIS"),
        ("status", "STATUS"),
    ],

    "RSO": [
        ("symptoms", "SYMPTOMS"),
        ("diagnosis", "DIAGNOSIS"),
        ("status", "STATUS"),
    ],


    "MC": [
        ("symptoms", "SYMPTOMS"),
        ("diagnosis", "DIAGNOSIS"),
        ("status", "STATUS"),
    ],


    "OTHERS": [
        ("description", "STATUS"),
    ],


    "STATUS_PERSONAL": [],

    "PERMANENT_STATUS": [
        ("status", "STATUS"),
    ],

    "TEMPORARY_STATUS": [
        ("status", "STATUS"),
        ("date_range", "DATE"),
    ],
}

# Separator line used in parade state output
PARADE_STATE_SEPARATOR = "-" * 56

# =========================
# CET CONFIG
# =========================

# Optional keywords for CET filtering (future-proofing)
CET_KEYWORDS = [
    "CET"
]
