import datetime
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db
from .iith_nutrition import get_menu_for_day
from .nutrition_service import analyze_food

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Calorie Tracker API")

# Allow the frontend to call this API from any origin (dev + deployed).
# Tighten this to your actual frontend domain once deployed if you want.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/ui")
def serve_ui():
    return FileResponse("static/index.html")


class MealCreate(BaseModel):
    name: str
    calories: float
    protein: float = 0
    carbs: float = 0
    fat: float = 0

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("calories")
    @classmethod
    def calories_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Calories must be greater than 0")
        return v


@app.get("/")
def root():
    return {"message": "Calorie Tracker API is running"}


@app.post("/meals")
def add_meal(meal: MealCreate, db: Session = Depends(get_db)):
    db_meal = models.Meal(
        name=meal.name,
        calories=meal.calories,
        protein=meal.protein,
        carbs=meal.carbs,
        fat=meal.fat,
        date=datetime.date.today(),
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


@app.get("/meals")
def get_meals(db: Session = Depends(get_db)):
    meals = db.query(models.Meal).all()
    return meals


@app.get("/meals/summary")
def get_summary(db: Session = Depends(get_db)):
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=6)

    daily_totals = (
        db.query(models.Meal.date, func.sum(models.Meal.calories).label("total_calories"))
        .filter(models.Meal.date >= week_ago)
        .group_by(models.Meal.date)
        .all()
    )

    return [{"date": str(row.date), "calories": row.total_calories} for row in daily_totals]


@app.delete("/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
    return {"message": f"Meal {meal_id} deleted successfully"}


@app.post("/meals/analyze")
async def analyze_meal(food_name: str, quantity: float = 1.0, db: Session = Depends(get_db)):
    if quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be greater than 0")

    nutrition = analyze_food(food_name)
    db_meal = models.Meal(
        name=nutrition["name"],
        calories=round(nutrition["calories"] * quantity),
        protein=round(nutrition["protein"] * quantity, 1),
        carbs=round(nutrition["carbs"] * quantity, 1),
        fat=round(nutrition["fat"] * quantity, 1),
        date=datetime.date.today(),
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


@app.get("/menu/{day}/{meal_type}")
def menu(day: str, meal_type: str):
    """Look up the IITH mess menu for a given day (e.g. 'monday') and
    meal_type ('breakfast', 'lunch', 'dinner', or 'snacks')."""
    valid_days = {
        "sunday", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday",
    }
    valid_meal_types = {"breakfast", "lunch", "dinner", "snacks"}

    day_l = day.lower()
    meal_type_l = meal_type.lower()

    if day_l not in valid_days:
        raise HTTPException(status_code=400, detail=f"Invalid day: {day}")
    if meal_type_l not in valid_meal_types:
        raise HTTPException(status_code=400, detail=f"Invalid meal_type: {meal_type}")

    return get_menu_for_day(day_l, meal_type_l)