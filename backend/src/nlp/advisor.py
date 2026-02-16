"""NLP-based health advice generator for LimbGuard-Cortex.

When a foot is classified as **normal**, this module generates preventive
self-care advice (sugar maintenance, skin care, scheduling reminders) using
a lightweight language model.

When gangrene is detected, the RAG pipeline is used instead (see
``backend.src.rag.engine``).
"""

from typing import Dict

try:
    from backend.src.config import CLASS_NAMES
except ImportError:
    from src.config import CLASS_NAMES  # type: ignore


# ── Static advice templates ────────────────────────────────────────────────
# These provide reliable, medically-informed guidance without requiring a
# large generative model at inference time.

_NORMAL_ADVICE: Dict[str, str] = {
    "sugar_maintenance": (
        "Monitor your blood sugar levels regularly. Aim for fasting glucose "
        "between 80-130 mg/dL and post-meal glucose below 180 mg/dL. Keep a "
        "daily log and share it with your healthcare provider."
    ),
    "skin_care": (
        "Inspect your feet daily for cuts, blisters, or changes in skin color. "
        "Wash feet with lukewarm water and mild soap, then dry thoroughly, "
        "especially between the toes. Apply a fragrance-free moisturizer to "
        "prevent cracking, but avoid applying between the toes."
    ),
    "footwear": (
        "Wear well-fitting, supportive shoes and moisture-wicking socks. "
        "Avoid walking barefoot. Check the inside of your shoes for foreign "
        "objects before wearing them."
    ),
    "scheduling": (
        "Schedule a comprehensive foot examination with your healthcare "
        "provider at least once a year. If you have diabetes or peripheral "
        "vascular disease, more frequent check-ups (every 3-6 months) are "
        "recommended."
    ),
}

_GRADE_ADVICE: Dict[str, Dict[str, str]] = {
    "grade_1": {
        "urgency": "LOW-MODERATE",
        "action": (
            "Early-stage wound detected. Clean the area gently with saline "
            "and apply a sterile dressing. Schedule an appointment with your "
            "healthcare provider within the next 1-2 days for professional "
            "evaluation."
        ),
        "home_care": (
            "Keep the foot elevated when resting. Avoid putting pressure on "
            "the affected area. Monitor for signs of infection such as "
            "increased redness, warmth, swelling, or discharge."
        ),
    },
    "grade_2": {
        "urgency": "MODERATE",
        "action": (
            "A deeper wound has been detected that may involve underlying "
            "tissue. Seek medical attention within 24 hours. Do not attempt "
            "to debride the wound yourself."
        ),
        "home_care": (
            "Keep the wound covered with a sterile, moist dressing. Avoid "
            "bearing weight on the affected foot. Monitor your temperature "
            "for signs of systemic infection."
        ),
    },
    "grade_3": {
        "urgency": "HIGH",
        "action": (
            "Significant tissue involvement detected. Seek medical attention "
            "today. This grade of wound may require surgical debridement, "
            "antibiotics, or specialized wound care."
        ),
        "home_care": (
            "Do not walk on the affected foot. Keep the wound loosely covered "
            "and seek emergency care if you notice foul odor, spreading "
            "redness, or fever."
        ),
    },
    "grade_4": {
        "urgency": "CRITICAL",
        "action": (
            "Severe tissue damage detected. Seek emergency medical care "
            "immediately. This condition may require hospitalization, IV "
            "antibiotics, or surgical intervention."
        ),
        "home_care": (
            "Go to the nearest emergency department or call emergency "
            "services. Do not delay treatment."
        ),
    },
}


def generate_advice(classification: str) -> Dict[str, str]:
    """Return health advice based on the image *classification* label.

    Parameters
    ----------
    classification : str
        One of ``config.CLASS_NAMES`` (e.g. ``"normal"``, ``"grade_1"``).

    Returns
    -------
    dict[str, str]
        Keys describe the advice category; values are the advice text.
    """
    classification = classification.lower().strip()

    if classification == "normal":
        return {
            "status": "Normal – no signs of gangrene detected.",
            **_NORMAL_ADVICE,
        }

    if classification in _GRADE_ADVICE:
        info = _GRADE_ADVICE[classification]
        return {
            "status": f"Gangrene detected – {classification.replace('_', ' ')}.",
            "urgency": info["urgency"],
            "recommended_action": info["action"],
            "home_care": info["home_care"],
        }

    return {"status": f"Unknown classification: {classification}. Please consult a doctor."}
