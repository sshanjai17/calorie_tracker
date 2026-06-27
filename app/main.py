from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from pydantic import BaseModel
import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class MealCreate(BaseModel):
    name: str
    calories: float
    protein: float = 0
    carbs: float = 0
    fat: float = 0

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
        date=datetime.date.today()
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@app.get("/meals")
def get_meals(db: Session = Depends(get_db)):
    meals = db.query(models.Meal).all()
    return meals