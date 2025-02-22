import jwt.api_jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models import Category, UserProfile, Course, Lesson, Exam, Question, Certificate, RefreshToken
from schema import CategorySchema, UserProfileSchema, CourseSchema, LessonSchema, ExamSchema, QuestionSchema, \
CertificateSchema, UserLogin
from admin import setup_admin
from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timedelta, datetime, timezone

course_app = FastAPI(title='Course site')
setup_admin(course_app)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_password(plain_password, set_password):
    return password_context.verify(plain_password, set_password)


def get_password_hash(password):
    return password_context.hash(password)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@course_app.post('/register/')
async def register(user: UserProfileSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username==user.username).first()
    if user_db:
        raise HTTPException(status_code=400, detail="User is allready redistered")
    new_hash_pass = get_password_hash(user.password)
    new_user = UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone_number=user.phone_number,
        age=user.age,
        profile_picture=user.profile_picture,
        role=user.role,
        password=new_hash_pass
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"massage": "Saved"}


@course_app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Маалымат туура эмес")
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    user_db = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(user_db)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@course_app.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Маалымат туура эмес")
    db.delete(stored_token)
    db.commit()
    return {"message": "Сайттан чыктыныз"}


@course_app.post('/category/create/', response_model=CategorySchema)
async def create_category(category: CategorySchema, db: Session = Depends(get_db)):
    db_category = Category(category_name=category.category_name)
    db.add(db_category)
    db.refresh(db_category)
    return db_category


@course_app.get("/category/", response_model=List[CategorySchema])
async def list_category(db: Session = Depends(get_db)):
    return db.query(Category).all()


@course_app.get("/category/{category_id}/", response_model=CategorySchema)
async def detail_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id==category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return category


@course_app.put("/category/{category_id}/", response_model=CategorySchema)
async def update_category(category_id: int, category_data: CategorySchema,
                          db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id==category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    category.category_name=category_data.category_name
    db.commit()
    db.refresh(category)
    return category


@course_app.delete("/category/{category_id}/", response_model=CategorySchema)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id==category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    db.delete(category)
    db.commit()
    return category


# COURSE-----------------------------


@course_app.post('/course/create/', response_model=CourseSchema)
async def course_create(course: CourseSchema, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@course_app.get('/course/', response_model=List[CourseSchema])
async def course_get(db: Session = Depends(get_db)):
    return db.query(Course).all()


@course_app.get('/course/{course_id}/', response_model=CourseSchema)
async def course_get(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id==course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@course_app.put("/course_update/{course_id}/", response_model=CourseSchema)
async def course_update(course_id: int, course_data: CourseSchema, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id==course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in course_data.dict().items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


@course_app.delete("/course_delete/course_id}/", response_model=CourseSchema)
async def course_delete(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id==course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return course


# LESSON-----------------------------


@course_app.post('/lesson_post/', response_model=LessonSchema)
async def lesson_create(lesson: LessonSchema, db: Session = Depends(get_db)):
     db_lesson = Lesson(**lesson.dict())
     db.add(db_lesson)
     db.commit()
     db.refresh(db_lesson)
     return db_lesson


@course_app.get("/lesson/", response_model=List[LessonSchema])
async def lesson_get(db: Session = Depends(get_db)):
    return db.query(Lesson).all()


@course_app.get('/lesson/{lesson_id}/', response_model=LessonSchema)
async def lesson_detail(lesson_id: int,  db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id==lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail='Lesson is not faund')
    return lesson


@course_app.put('/lesson/{lesson_id}/', response_model=LessonSchema)
async def lesson_put(lesson_id: int, lessons_data: LessonSchema,  db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id==lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail='Lesson is not faund')
    for key, value in lessons_data.dict().items():
        setattr(lesson, key, value)
    db.commit()
    db.refresh(lesson)
    return lesson


@course_app.delete('/lesson/{lesson_id}/', response_model=LessonSchema)
async def lesson_delete(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id==lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail='Lesson is not faund')
    db.delete(lesson)
    db.commit()
    return lesson

# Exam ------------------

@course_app.post('/exam_post/', response_model=ExamSchema)
async def exam_create(lesson: ExamSchema, db: Session = Depends(get_db)):
     db_exam = Exam(**lesson.dict())
     db.add(db_exam)
     db.commit()
     db.refresh(db_exam)
     return db_exam


@course_app.get("/exam/", response_model=List[ExamSchema])
async def exam_get(db: Session = Depends(get_db)):
    return db.query(Exam).all()


@course_app.get('/exam/{exam_id}/', response_model=ExamSchema)
async def exam_detail(exam_id: int,  db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id==exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail='Exam is not faund')
    return exam


@course_app.put('/exam/{exam_id}/', response_model=ExamSchema)
async def exam_detail(exam_id: int, exam_data: ExamSchema, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id==exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail='Exam is not faund')
    for key, value in exam_data.dict().items():
        setattr(exam, key, value)
    db.commit()
    db.refresh(exam)
    return exam


@course_app.delete('/exam/{exam_id}/', response_model=ExamSchema)
async def exam_detail(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id==exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail='Exam is not faund')
    db.delete(exam)
    db.commit()
    return exam

@course_app.post('/question/create/', response_model=QuestionSchema)
async def create_question(question: QuestionSchema, db: Session = Depends(get_db)):
    db_question = Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@course_app.get('/question/', response_model=List[QuestionSchema])
async def list_question(db: Session = Depends(get_db)):
    return db.query(Question).all()


@course_app.get('/question/{question_id}/', response_model=QuestionSchema)
async def detail_question(question_id: int, db:Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id==question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail='Question not found')
    return question


@course_app.put('/question/{question_id}/', response_model=QuestionSchema)
async def update_question(question_id: int,
                        question_data: QuestionSchema,
                        db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id==question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail='Question not found')
    for question_key, question_value in question_data.dict().items():
        setattr(question, question_key, question_value)
    db.commit()
    db.refresh(question)
    return question


@course_app.delete('/question/{question_id}')
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id==question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail='Question not found')
    db.delete(question)
    db.commit()
    return {'message': 'This Question is Deleted'}


@course_app.post('/certificate/create/', response_model=CertificateSchema)
async def create_certificate(certificate: CertificateSchema, db: Session = Depends(get_db)):
    db_certificate = Certificate(**certificate.dict())
    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)
    return db_certificate


@course_app.get('/certificate/', response_model=List[CertificateSchema])
async def list_certificate(db: Session = Depends(get_db)):
    return db.query(Certificate).all()


@course_app.get('/certificate/{certificate_id}/', response_model=CertificateSchema)
async def detail_certificate(certificate_id: int, db:Session = Depends(get_db)):
    certificate = db.query(Certificate).filter(Certificate.id==certificate_id).first()
    if certificate is None:
        raise HTTPException(status_code=404, detail='Certificate not found')
    return certificate


@course_app.put('/certificate/{certificate_id}/', response_model=CertificateSchema)
async def update_certificate(certificate_id: int,
                        certificate_data: CertificateSchema,
                        db: Session = Depends(get_db)):
    certificate = db.query(Certificate).filter(Certificate.id==certificate_id).first()
    if certificate is None:
        raise HTTPException(status_code=404, detail='Certificate not found')
    for certificate_key, certificate_value in certificate_data.dict().items():
        setattr(certificate, certificate_key, certificate_value)
    db.commit()
    db.refresh(certificate)
    return certificate


@course_app.delete('/certificate/{certificate_id}')
async def delete_certificate(certificate_id: int, db: Session = Depends(get_db)):
    certificate = db.query(Certificate).filter(Certificate.id==certificate_id).first()
    if certificate is None:
        raise HTTPException(status_code=404, detail='Certificate not found')
    db.delete(certificate)
    db.commit()
    return {'message': 'This Certificate is Deleted'}
