# models/workflow_model.py
from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from dbconfig.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    data = Column(JSON, nullable=True)
    graph = Column(JSON, nullable=True)

    # relationships
    user = relationship("User", back_populates="workflows")
    knowledges = relationship("Knowledge", back_populates="workflow", cascade="all, delete")
