from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from constants.configuration import Configuration

class UserAuth(Configuration.BASE):
    __tablename__ = 'user_auth'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    username = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)

    user = relationship('User', back_populates='auth')