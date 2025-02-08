from pydantic import BaseModel
from datetime import datetime, time


class UserProfile(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    age: int
    profile_picture: str


class Network(BaseModel):
    network_name: str
    network_link: str


class Category(BaseModel):
    category_name: str


class Course(BaseModel):
    course_name: str
    description: str
    category: str
    author: str
    level: tuple[str, str]
    price: int
    type_course: tuple[str, str]
    created_at: datetime
    updated_at: datetime
    course_certificate: bool


class Lesson(BaseModel):
    title: str
    video_url: str
    video: str or None
    content: str or None


class Assignment(BaseModel):
    title: str
    description: str
    due_date: datetime
    course: str
    students: str


class Exam(BaseModel):
    title: str
    course: str
    end_time: time


class Questions(BaseModel):
    exam: str
    title: str
    score: int


class Option(BaseModel):
    questions: str
    variant: str
    option_check: bool


class Certificate(BaseModel):
    student: str
    course: str
    issued_at: datetime
    certificate_url: str or None


class CourseReview(BaseModel):
    course: str
    user: str
    text: str
    stars: int


class TeacherRating(BaseModel):
    teacher: str
    user: str
    stars: int


class History(BaseModel):
    student: str
    course: str
    date: datetime


class Cart(BaseModel):
    student: str


class CartItem(BaseModel):
    cart: str
    course: str


class Favorite(BaseModel):
    student: str


class FavoriteItem(BaseModel):
    favorite: str
    course: str
