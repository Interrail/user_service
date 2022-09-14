import enum

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Enum
from sqlalchemy.sql.expression import text

# This is a special import for ENUM strictly because I am using postgres DB

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
