from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base
import datetime

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    date = Column(Date, default=datetime.date.today)