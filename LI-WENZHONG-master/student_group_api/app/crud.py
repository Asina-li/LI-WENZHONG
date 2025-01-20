
from sqlalchemy.orm import Session
import models
import schemas


def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(name=student.name)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    if student:
        db.delete(student)
        db.commit()
    return student


def get_group(db: Session, group_id: int):
    return db.query(models.Group).filter(models.Group.id == group_id).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Group).offset(skip).limit(limit).all()

def create_group(db: Session, group: schemas.GroupCreate):
    db_group = models.Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_group(db: Session, group_id: int):
    group = get_group(db, group_id)
    if group:
        db.delete(group)
        db.commit()
    return group

def add_student_to_group(db: Session, student_id: int, group_id: int):
    student = get_student(db, student_id)
    group = get_group(db, group_id)
    if student and group:
        group.students.append(student)
        db.commit()
        return True
    return False

def remove_student_from_group(db: Session, student_id: int, group_id: int):
    student = get_student(db, student_id)
    group = get_group(db, group_id)
    if student and group:
        group.students.remove(student)
        db.commit()
        return True
    return False

def get_students_in_group(db: Session, group_id: int):
    group = get_group(db, group_id)
    if group:
        return group.students
    return []

def transfer_student(db: Session, student_id: int, from_group_id: int, to_group_id: int):
    student = get_student(db, student_id)
    from_group = get_group(db, from_group_id)
    to_group = get_group(db, to_group_id)
    if student and from_group and to_group:
        if student in from_group.students:
            from_group.students.remove(student)
            to_group.students.append(student)
            db.commit()
            return True
    return False
