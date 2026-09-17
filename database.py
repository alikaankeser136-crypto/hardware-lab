from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./hardware_lab.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    name = Column(String)
    picture = Column(String)

class HardwareItem(Base):
    __tablename__ = "hardware"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)  # 'GPU' veya 'CPU'
    brand = Column(String)     # 'NVIDIA', 'AMD', 'Intel'
    specs = Column(Text)       # JSON veya açıklayıcı metin
    score = Column(Float)       # Performans puanı

    reviews = relationship("Review", back_populates="item")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    hardware_id = Column(Integer, ForeignKey("hardware.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # 1 - 5 yıldız
    comment = Column(Text)

    item = relationship("HardwareItem", back_populates="reviews")
    user = relationship("User")

def init_db():
    Base.metadata.create_all(bind=engine)