from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class UserResponse(BaseModel):
    message: str
    username: str

    class Config:
        orm_mode = True

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"))
    reservation_details = Column(String)

    user = relationship("User")

class ReservationResponse(BaseModel):
    message: str
    username: str
    reservation_details: str

    class Config:
        orm_mode = True
