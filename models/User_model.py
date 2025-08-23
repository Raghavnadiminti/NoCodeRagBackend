# models/user_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from dbconfig.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    mobile_number = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # relationships
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete")
    knowledges = relationship("Knowledge", back_populates="user", cascade="all, delete")
