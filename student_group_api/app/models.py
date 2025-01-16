# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# 学生和组的多对多关系关联表
association_table = Table(
    'association',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    groups = relationship('Group', secondary=association_table, back_populates='students')

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    students = relationship('Student', secondary=association_table, back_populates='groups')
