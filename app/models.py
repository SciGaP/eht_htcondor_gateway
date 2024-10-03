from app import db

from flask_login import UserMixin
import uuid
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    nickname = Column(String)
    given_name = Column(String)
    family_name = Column(String)
    password = Column(String)
    email = Column(String, unique=False, nullable=False)
    profile_picture = Column(String)
    # two values: "local", "cilogon"
    account_type = Column(String)

    def __repr__(self):
        return f"<{self.id}>"