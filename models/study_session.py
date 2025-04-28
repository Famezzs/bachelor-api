from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from constants.configuration import Configuration

class StudySession(Configuration.BASE):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'))
    length_minutes = Column(Integer, nullable=False)
    reactions_total = Column(Integer, nullable=False)
    
    student = relationship('Student', back_populates='sessions')
