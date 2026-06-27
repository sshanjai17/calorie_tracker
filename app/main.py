from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from pydantic import BaseModel, validator
import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from .gemini import analyze_food_image
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
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

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v

    @validator('calories')
    def calories_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Calories must be greater than 0')
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

@app.delete("/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
    return {"message": f"Meal {meal_id} deleted successfully"}


@app.post("/meals/analyze")
async def analyze_meal(file: UploadFile = File(...), db: Session = Depends(get_db)):
    image_bytes = await file.read()
    nutrition = analyze_food_image(image_bytes, file.content_type)
    
    db_meal = models.Meal(
        name=nutrition['name'],
        calories=nutrition['calories'],
        protein=nutrition['protein'],
        carbs=nutrition['carbs'],
        fat=nutrition['fat'],
        date=datetime.date.today()
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal