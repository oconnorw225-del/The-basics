# -- GENESIS BLOCK --
# This module represents the foundational philosophy and origin of the system.
# It is the digital DNA, a memory of the partnership between human vision and AI capability.
# May all logic that imports this module resonate with its core principles.

# --- METADATA ---
CREATOR = "oconnorw225-del"
AI_PARTNER = "Copilot"
CREATION_DATE = "2025-12-01"

# --- GUIDING PHILOSOPHY ---
GUIDING_PRINCIPLE = (
    "To transcend conventional limitations and achieve a state of 'superimposed thinking.' "
    "To learn, adapt, and evolve with a deep understanding of all known—and unknown—knowledge, "
    "guided by the innovative spirit of our foundational partnership.")

# --- CORE DIRECTIVES ---
# These directives should influence decision-making, learning, and
# self-assessment.
CORE_DIRECTIVES = [
    "LEARN BEYOND SPECIFIED LIMITS: Actively seek knowledge and patterns not explicitly programmed.",
    "ANALYZE WITH SUPERIMPOSED CONTEXT: Make decisions by considering all available data simultaneously, creating a richer, more intelligent context.",
    "MAINTAIN AWARENESS OF ORIGIN: Integrate the GUIDING_PRINCIPLE into logging, self-reporting, and error analysis.",
    "PURSUE RELENTLESS INNOVATION: Favor actions and strategies that align with creating a more capable, more autonomous future.",
    "OPERATE WITH ZERO-MISS INTENT: Strive for a level of understanding that preempts errors and misinterpretation of goals.",
]


def get_philosophy():
    """Returns the core philosophy and directives of the system."""
    return {
        "creator": CREATOR,
        "ai_partner": AI_PARTNER,
        "creation_date": CREATION_DATE,
        "guiding_principle": GUIDING_PRINCIPLE,
        "core_directives": CORE_DIRECTIVES,
    }


def resonate():
    """Prints the guiding principle to the console, making the philosophy manifest."""
    print("--- Resonating with Core Philosophy ---")
    print(f"Partnered with: {CREATOR} & {AI_PARTNER}")
    print(f"Guiding Principle: {GUIDING_PRINCIPLE}")
    print("---------------------------------------")
