from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    mail = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    es_admin = Column(Boolean, default=False)
