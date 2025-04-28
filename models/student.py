from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .user import User
from models.study_session import StudySession

class Student(User):
    __tablename__ = 'students'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    assigned_teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': User.UserType.STUDENT,
    }
    
    teacher = relationship(
        'Teacher',
        back_populates='students',
        foreign_keys=[assigned_teacher_id]
    )
    sessions = relationship('StudySession', back_populates='student')
    grades = relationship('Grade', back_populates='student')
