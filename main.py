from datetime import datetime, timedelta
from typing import Union
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import JWTError, jwt

from constants.configuration import Configuration
from services.database_engine import DatabaseEngine
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.grade import Grade
from models.study_session import StudySession
from models.user_auth import UserAuth
from pydantics.auth_pydantic import AuthPydantic
from pydantics.user_pydantic import UserPydantic
from pydantics.student_pydantic import StudentPydantic
from pydantics.grade_pydantic import GradePydantic
from pydantics.session_pydantic import SessionPydantic
from pydantics.chat_pydantic import ChatPydantic

database_engine = DatabaseEngine(Configuration.DATABASE_CONNECTION_PARAMETERS)
app = FastAPI()
bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=[Configuration.CRYPT_SCHEME], deprecated="auto")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: DBSession = Depends(database_engine.get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, Configuration.SECRET_KEY, algorithms=[Configuration.ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("type")
        if user_id is None or user_type is None:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).get(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_student(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(database_engine.get_db),
) -> Student:
    if user.user_type != User.UserType.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint",
        )
    student = db.query(Student).get(user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student record not found",
        )
    return student

def get_current_teacher(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(database_engine.get_db),
) -> Teacher:
    if user.user_type != User.UserType.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint",
        )
    teacher = db.query(Teacher).get(user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found",
        )
    return teacher

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=Configuration.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, Configuration.SECRET_KEY, algorithm=Configuration.ALGORITHM)

@app.post(
    "/api/v1/users",
    response_model=Union[UserPydantic.UserResponse, StudentPydantic.StudentResponse],
    summary="Create a new user (student or teacher)",
)
def create_user(
    req: Union[UserPydantic.UserCreate, StudentPydantic.StudentCreate],
    db: DBSession = Depends(database_engine.get_db),
):
    if db.query(UserAuth).filter_by(username=req.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    try:
        if req.user_type == User.UserType.STUDENT:
            student = Student(
                first_name=req.first_name,
                last_name=req.last_name,
                assigned_teacher_id=getattr(req, "assigned_teacher_id", None),
            )
            db.add(student)
            db.flush()
            auth = UserAuth(
                user_id=student.id,
                username=req.username,
                password_hash=pwd_context.hash(req.password)
            )
            db.add(auth)
            db.commit()
            db.refresh(student)
            return student
        elif req.user_type == User.UserType.TEACHER:
            teacher = Teacher(
                first_name=req.first_name,
                last_name=req.last_name,
            )
            db.add(teacher)
            db.flush()
            auth = UserAuth(
                user_id=teacher.id,
                username=req.username,
                password_hash=pwd_context.hash(req.password)
            )
            db.add(auth)
            db.commit()
            db.refresh(teacher)
            return teacher
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user type",
            )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

@app.post(
    "/api/v1/authenticate",
    response_model=AuthPydantic.AuthResponse,
    summary="Authenticate user and receive a bearer token",
)
def login_for_access_token(
    req: AuthPydantic.AuthRequest,
    db: DBSession = Depends(database_engine.get_db),
):
    auth = db.query(UserAuth).filter_by(username=req.username).first()
    if not auth or not pwd_context.verify(req.password, auth.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    user = db.query(User).get(auth.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    access_token = create_access_token({
        "sub": str(auth.user_id),
        "type": user.user_type
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user.user_type
    }

@app.get(
    "/api/v1/grades",
    response_model=list[GradePydantic.GradeResponse],
    summary="Get grades assigned by the current teacher",
)
def get_grades(
    filters: GradePydantic.GradeFilter = Depends(),
    current_teacher: Teacher = Depends(get_current_teacher),
    db: DBSession = Depends(database_engine.get_db),
):
    query = db.query(Grade).filter(
        Grade.grader_teacher_id == current_teacher.id
    )
    
    if filters.student_id:
        query = query.filter(Grade.graded_student_id == filters.student_id)
    
    if filters.start_date:
        query = query.filter(Grade.date >= filters.start_date)
    
    if filters.end_date:
        query = query.filter(Grade.date <= filters.end_date)
    
    if filters.min_score is not None:
        query = query.filter(Grade.score >= filters.min_score)
    
    if filters.max_score is not None:
        query = query.filter(Grade.score <= filters.max_score)
    
    grades = query.order_by(Grade.date.desc()).all()
    
    return grades

@app.post(
    "/api/v1/grades",
    response_model=GradePydantic.GradeResponse,
    summary="Create a new grade record (teacher only)",
    status_code=status.HTTP_201_CREATED,
)
def create_grade(
    grade_data: GradePydantic.GradeCreate,
    current_teacher: Teacher = Depends(get_current_teacher),
    db: DBSession = Depends(database_engine.get_db),
):
    student = db.query(Student).get(grade_data.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    try:
        grade = Grade(
            date=grade_data.date,
            graded_student_id=grade_data.student_id,
            grader_teacher_id=current_teacher.id,
            score=grade_data.score,
            comments=grade_data.comments,
        )
        db.add(grade)
        db.commit()
        db.refresh(grade)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create grade record",
        )
    
    return grade

@app.get(
    "/api/v1/sessions",
    response_model=list[SessionPydantic.SessionResponseExtended],
    summary="Get study sessions for teacher's students",
)
def get_teacher_sessions(
    filters: SessionPydantic.SessionFilter = Depends(),
    current_teacher: Teacher = Depends(get_current_teacher),
    db: DBSession = Depends(database_engine.get_db),
):
    query = db.query(StudySession).join(
        Student,
        StudySession.student_id == Student.id
    ).filter(
        Student.assigned_teacher_id == current_teacher.id
    )
    
    if filters.student_id:
        query = query.filter(StudySession.student_id == filters.student_id)
    
    if filters.start_date:
        query = query.filter(StudySession.date >= filters.start_date)
    
    if filters.end_date:
        query = query.filter(StudySession.date <= filters.end_date)
    
    if filters.min_duration:
        query = query.filter(StudySession.length_minutes >= filters.min_duration)
    
    if filters.max_duration:
        query = query.filter(StudySession.length_minutes <= filters.max_duration)
    
    sessions = query.order_by(StudySession.date.desc()).all()
    
    response = []
    for session in sessions:
        student = db.query(Student).get(session.student_id)
        response.append({
            "status": "success",
            "session_id": session.id,
            "date": session.date,
            "student_id": session.student_id,
            "length_minutes": session.length_minutes,
            "reactions_total": session.reactions_total,
            "student_name": f"{student.first_name} {student.last_name}"
        })
    
    return response

@app.post(
    "/api/v1/sessions",
    response_model=SessionPydantic.SessionResponse,
    summary="Save a study session for the authenticated student",
)
def save_session(
    req: SessionPydantic.SessionRequest,
    current_student: Student = Depends(get_current_student),
    db: DBSession = Depends(database_engine.get_db),
):
    if req.student_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="student_id does not match token subject",
        )
    session_entry = StudySession(
        date=req.date,
        student_id=current_student.id,
        length_minutes=req.length_minutes,
        reactions_total=req.reactions_total
    )
    db.add(session_entry)
    db.commit()
    return {"status": "success", "session_id": session_entry.id}

@app.post(
    "/api/v1/chat",
    response_model=ChatPydantic.ChatResponse,
    summary="Send a prompt to ChatGPT on behalf of the authenticated student",
)
def chat(
    req: ChatPydantic.ChatRequest,
    current_student: Student = Depends(get_current_student),
):
    import openai

    openai.api_key = Configuration.OPENAI_AI_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": req.prompt}]
    )

    return {"response": response.choices[0].message.content}