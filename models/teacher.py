from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .user import User

class Teacher(User):
    __tablename__ = 'teachers'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': User.UserType.TEACHER,
    }
    
    students = relationship(
        'Student',
        back_populates='teacher',
        foreign_keys='Student.assigned_teacher_id'
    )
    grades_given = relationship('Grade', back_populates='grader')
