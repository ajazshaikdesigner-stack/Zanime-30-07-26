from dataclasses import dataclass, field


@dataclass
class StoryVersion:
    version_id: str
    timestamp: float
    ai_model: str
    prompt: str
    result: str


@dataclass
class StoryModel:
    title: str = "Untitled Story"
    tagline: str = ""
    summary: str = ""
    content: str = ""

    characters: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    props: list[str] = field(default_factory=list)

    duration_est: str = "00:00:00"
    rating: str = "G"
    keywords: list[str] = field(default_factory=list)
    mood: str = ""
    moral: str = ""

    is_locked: bool = False

    history: list[StoryVersion] = field(default_factory=list)
