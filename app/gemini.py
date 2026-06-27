import random

def analyze_food_image(image_bytes: bytes, mime_type: str = "image/jpeg"):
    mock_foods = [
        {"name": "Rice bowl", "calories": 350, "protein": 8, "carbs": 72, "fat": 2},
        {"name": "Chicken curry", "calories": 420, "protein": 35, "carbs": 18, "fat": 22},
        {"name": "Dal tadka", "calories": 280, "protein": 14, "carbs": 40, "fat": 8},
        {"name": "Paneer butter masala", "calories": 380, "protein": 18, "carbs": 22, "fat": 26},
        {"name": "Idli sambar", "calories": 200, "protein": 6, "carbs": 38, "fat": 3},
        {"name": "Pizza slice", "calories": 285, "protein": 12, "carbs": 36, "fat": 10},
    ]
    return random.choice(mock_foods)