"""
Nutrition lookup service.

NOTE: This originally called the Gemini Vision API to analyze food photos.
That approach was abandoned due to deprecated client libraries and free-tier
quota limits that made it unreliable for a live demo. It was replaced with a
local lookup against the IITH mess menu (see iith_nutrition.py), which is
free, fast, and has zero external dependencies/rate limits.
"""

from .iith_nutrition import lookup_food


def analyze_food(food_name: str):
    return lookup_food(food_name)