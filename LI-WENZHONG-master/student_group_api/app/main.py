# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)


@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return db_student


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    result = crud.delete_student(db, student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"detail": "Студент удален"}


@app.get("/students/", response_model=List[schemas.Student])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students


@app.post("/groups/", response_model=schemas.Group)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    return crud.create_group(db=db, group=group)


@app.get("/groups/{group_id}", response_model=schemas.Group)
def read_group(group_id: int, db: Session = Depends(get_db)):
    db_group = crud.get_group(db, group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return db_group


@app.delete("/groups/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    result = crud.delete_group(db, group_id)
    if not result:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return {"detail": "Группа удалена"}


@app.get("/groups/", response_model=List[schemas.Group])
def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = crud.get_groups(db, skip=skip, limit=limit)
    return groups


@app.post("/groups/{group_id}/students/{student_id}")
def add_student_to_group(group_id: int, student_id: int, db: Session = Depends(get_db)):
    success = crud.add_student_to_group(db, student_id, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ни один студент или группа не найдены")
    return {"detail": "Студент добавлен в группу"}


@app.delete("/groups/{group_id}/students/{student_id}")
def remove_student_from_group(group_id: int, student_id: int, db: Session = Depends(get_db)):
    success = crud.remove_student_from_group(db, student_id, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ни один студент или группа не найдены")
    return {"detail": "Студент удален из группы"}


@app.get("/groups/{group_id}/students/", response_model=List[schemas.Student])
def get_students_in_group(group_id: int, db: Session = Depends(get_db)):
    students = crud.get_students_in_group(db, group_id)
    if students is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return students


@app.post("/students/{student_id}/transfer/")
def transfer_student(student_id: int, from_group_id: int, to_group_id: int, db: Session = Depends(get_db)):
    success = crud.transfer_student(db, student_id, from_group_id, to_group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Студент или группа не найдены, или студент не входит в исходную группу")
    return {"detail": "Студент перевелся"}
