# admin.py
from sqladmin import Admin, ModelView
from models import UserProfile, Course, Category, Lesson, Exam, Question, Certificate  # Импортируем модель User
from database import engine  # Импортируем engine из database.py


class UserAdmin(ModelView, model=UserProfile):
    column_list = [column.name for column in UserProfile.__table__.columns]


class CourseAdmin(ModelView, model=Course):
    column_list = [column.name for column in Course.__table__.columns]


class CategoryAdmin(ModelView, model=Category):
    column_list = [column.name for column in Category.__table__.columns]


class LessonAdmin(ModelView, model=Lesson):
    column_list = [column.name for column in Lesson.__table__.columns]


class ExamAdmin(ModelView, model=Exam):
    column_list = [column.name for column in Exam.__table__.columns]


class QuestionAdmin(ModelView, model=Question):
    column_list = [column.name for column in Question.__table__.columns]


class CertificateAdmin(ModelView, model=Certificate):
    column_list = [column.name for column in Certificate.__table__.columns]


def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(LessonAdmin)
    admin.add_view(ExamAdmin)
    admin.add_view(QuestionAdmin)
    admin.add_view(CertificateAdmin)