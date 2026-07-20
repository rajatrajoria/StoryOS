from enum import StrEnum


class AgentName(StrEnum):
    PLANNER = "planner"
    RESEARCH = "research"
    ANGLE = "angle"
    OUTLINE = "outline"
    DRAFT = "draft"
    CRITIC = "critic"
    FACT_CHECK = "fact_check"
    VOICE = "voice"
    VISUAL = "visual"