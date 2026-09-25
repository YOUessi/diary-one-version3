"""Owner-approved Chapter coherence guidance for the existing S07 call.

This policy changes the model's grouping brief only. It does not pretend that
deterministic code can prove a semantic story, add a second reviewer call, or
turn scene words and import positions into runtime grouping gates.
"""


POLICY_VERSION = "DIARY_ONE_X02_CHAPTER_COHERENCE_V01"
POLICY_FIELD = "chapter_coherence_policy_version"


def prompt_instruction(context):
    """Return the active, scene-neutral grouping boundary."""
    if context.get(POLICY_FIELD) != POLICY_VERSION:
        return ""
    return (
        "Apply an experience-first Chapter boundary. Each Chapter must center on one "
        "focal experience supported by the supplied facts. A shared broad topic, object "
        "category, visual style, mood or setting label may support a group, but is never "
        "sufficient by itself. Cross-setting members are allowed only when their facts "
        "support one common activity, event, interaction or focal exploration thread. "
        "That support may connect transitively across the beat_map; not every pair must "
        "look alike, but every member must connect to the focal experience through its "
        "cited facts. Mere absence of a contradiction is not connection evidence. "
        "Do not infer that thread from shared labels or import order. Before submitting "
        "each Chapter, inspect its thesis and reason: if they describe two or more distinct "
        "episodes whose only connection is a theme or aesthetic, do not combine them. "
        "Propose a supported subgroup when it has at least three KEEP observations; otherwise "
        "omit that Chapter rather than padding it. Omitted Chapter material remains available "
        "to the existing Aha search when it has independent value. "
    )
