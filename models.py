from datetime import datetime
from typing import Optional
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, List, DECIMAL, DateTime, func, Integer


class UserProfile(Base):
    __tablename__ = "userprofile"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(40))
    last_name: Mapped[str] = mapped_column(String(40))
    username: Mapped[str] = mapped_column(String(40), unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int]
    profile_picture: Mapped[str] = mapped_column(nullable=True)
    networks: Mapped[List['Network']] = relationship(back_populates="user",
                                                    cascade="all, delete-orphan")

    author_course: Mapped[List['Course']] = relationship(back_populates="author",
                                                         cascade="all, delete-orphan")
    course_review: Mapped[List["CourseReview"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")
    user_history: Mapped[List["History"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")


class Network(Base):
    __tablename__ = "network"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    network_name: Mapped[str] = mapped_column(String(65))
    network_link: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("userprofile.id"))
    user: Mapped["UserProfile"] = relationship(back_populates="networks")


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(32), unique=True)
    category_course: Mapped[List["Course"]] = relationship(back_populates="category",
                                                           cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    course_name: Mapped[int] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    category: Mapped['Category'] = relationship(back_populates='category_course')
    author_id: Mapped[int] = mapped_column(ForeignKey("userprofile.id"))
    author: Mapped['UserProfile'] = relationship(back_populates="author_course")
    level: Mapped[str] = mapped_column(String(32))
    price: Mapped[float] = mapped_column(DECIMAL(8, 2))
    crested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    course_certificate: Mapped[bool] = mapped_column(default=True)
    course_image: Mapped[str] = mapped_column(nullable=True)
    course_lesson: Mapped[List["Lesson"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan")

    exams: Mapped[List["Exam"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan")

    certificates: Mapped[List["Certificate"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan")

    review: Mapped[List["CourseReview"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan")
    history: Mapped[List["History"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan")




class Lesson(Base):
    __tablename__ = "lesson"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64))
    video_url: Mapped[str] = mapped_column(nullable=True)
    video: Mapped[str] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column(nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped[List["Course"]] = relationship(back_populates='course_lesson')
    assignments: Mapped[List["Assignment"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan")


class Assignment(Base):
    __tablename__ = "assignment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates='assignments')
    students: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lesson.id'), nullable=True)
    lesson: Mapped["Lesson"] = relationship(back_populates='assignments')


class Exam(Base):
    __tablename__ = "exam"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64))
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates='exams')
    end_time: Mapped[datetime] = mapped_column(DateTime)
    questions: Mapped[List["Question"]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan")



class Question(Base):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey('exam.id'))
    exam: Mapped["Exam"] = relationship(back_populates='questions')
    title: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer)
    options: Mapped[List["Option"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "option"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"))
    question: Mapped["Question"] = relationship(back_populates="options")
    variant: Mapped[str] = mapped_column(String(64))
    option_check: Mapped[bool] = mapped_column()




class Certificate(Base):
    __tablename__ = "certificate"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    student: Mapped["UserProfile"] = relationship()
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates="certificates")
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    certificate_url: Mapped[str] = mapped_column(String(64))


class CourseReview(Base):
    __tablename__ = "coursereview"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates="review")
    user_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    user: Mapped["UserProfile"] = relationship(back_populates="course_review")
    text: Mapped[str] = mapped_column(Text)
    stars: Mapped[int] = mapped_column(Integer)


class History(Base):
    __tablename__ = "history"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    user: Mapped["UserProfile"] = relationship(back_populates="user_history")
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped["Course"] = relationship(back_populates="history")
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


