# models/knowledge_model.py
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from dbconfig.database import Base

class Knowledge(Base):
    __tablename__ = "knowledges"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="CASCADE"))
    pdfId = Column(String, nullable=False)


    # relationships
    user = relationship("User", back_populates="knowledges")
    workflow = relationship("Workflow", back_populates="knowledges")
