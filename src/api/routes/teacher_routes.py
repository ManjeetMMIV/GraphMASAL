from fastapi import APIRouter
from src.api.controllers.teacher_controller import (
    AddStudentRequest,
    list_teacher_students_logic,
    add_student_to_teacher_logic,
    remove_student_from_teacher_logic,
    get_student_progress_logic
)

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])

@router.get("/{teacher_id}/students")
async def list_teacher_students(teacher_id: str):
    return list_teacher_students_logic(teacher_id)

@router.post("/{teacher_id}/students")
async def add_student_to_teacher(teacher_id: str, req: AddStudentRequest):
    return add_student_to_teacher_logic(teacher_id, req)

@router.delete("/{teacher_id}/students/{student_id}")
async def remove_student_from_teacher(teacher_id: str, student_id: str):
    return remove_student_from_teacher_logic(teacher_id, student_id)

@router.get("/student/{student_id}/progress")
async def get_student_progress(student_id: str):
    return get_student_progress_logic(student_id)
