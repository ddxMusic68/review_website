from dataclasses import dataclass, field
from typing import Optional

OUT_OF_STARS = 10

FILMING_DESC = "How is the camera work, lighting, and shot composition?"
STORYTELLING_DESC = "How engaging and well-structured is the narrative?"
HOOK_DESC = "How well does the video capture attention in the first moments?"
THEME_DESC = "How clearly and effectively is the central theme conveyed?"
PACING_DESC = "How well does the video sustain momentum and timing?"


@dataclass
class StarRating:
    stars: int
    out_of_stars: int = OUT_OF_STARS

    def __post_init__(self):
        if not (0 <= self.stars <= self.out_of_stars):
            raise ValueError(
                f"stars must be between 0 and {self.out_of_stars}, got {self.stars}"
            )


@dataclass
class Category:
    name: str
    description: str
    review: str = ""
    rating: Optional[StarRating] = None


@dataclass
class Review:
    categories: dict = field(default_factory=dict)

    @classmethod
    def default(cls):
        specs = {
            "filming": FILMING_DESC,
            "storytelling": STORYTELLING_DESC,
            "hook": HOOK_DESC,
            "theme": THEME_DESC,
            "pacing": PACING_DESC,
        }
        categories = {
            name: Category(name=name, description=description)
            for name, description in specs.items()
        }
        return cls(categories=categories)


@dataclass
class YtVideo:
    video_id: str
    star_review: Optional[StarRating] = None
    review: Review = field(default_factory=Review.default)