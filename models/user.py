from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from constants.configuration import Configuration

class User(Configuration.BASE):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    from constants.user_type import UserType
    user_type = Column(SQLAlchemyEnum(UserType), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': UserType.UNDEFINED,
        'polymorphic_on': user_type
    }
    
    auth = relationship('UserAuth', back_populates='user', uselist=False)