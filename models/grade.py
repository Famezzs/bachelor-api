from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from constants.configuration import Configuration
    
class Grade(Configuration.BASE):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=False)
    comments = Column(String(150), nullable=True)
    graded_student_id = Column(Integer, ForeignKey('students.id'))
    grader_teacher_id = Column(Integer, ForeignKey('teachers.id'))

    student = relationship('Student', back_populates='grades')
    grader = relationship('Teacher', back_populates='grades_given')
