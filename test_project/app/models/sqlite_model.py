from sqlalchemy import Boolean, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Определяем модель данных.
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    is_active = Column(Boolean)
    is_deleted = Column(Boolean)
