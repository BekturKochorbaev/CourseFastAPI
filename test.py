ROLE_CHOICES = (
    ('teacher', 'teacher'),
    ('student', 'student')
)

STATUS_CHOICES = (
    ("легкий", 'легкий'),
    ('средний', 'средний'),
    ('сложный', 'сложный')
)


class UserProfile(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(15),
                                                       MaxValueValidator(60)],
                                           null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def str(self):
        return f'{self.first_name}, {self.last_name}'


class Network(models.Model):
    network_name = models.CharField(max_length=32)
    network_link = models.URLField()
    title = models.CharField(max_length=32, null=True, blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def str(self):
        return f'{self.user}, {self.network_name}'


class Teacher(UserProfile):
    bio = models.TextField()
    DAYS_CHOICES = (
        ('ПН', 'ПН'),
        ('ВТ', 'ВТ'),
        ('СР', 'СР'),
        ('ЧТ', 'ЧТ'),
        ('ПТ', 'ПТ'),
        ('СБ', 'СБ')
    )
    work_days = MultiSelectField(max_length=16, choices=DAYS_CHOICES, max_choices=6)
    subjects = models.TextField()
    experience = models.PositiveSmallIntegerField(validators=[MaxValueValidator(40)])
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='teacher')

    def str(self):
        return f'{self.first_name}, {self.role}'

    class Meta:
        verbose_name_plural = "teachers"


class Student(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='student')

    def str(self):
        return f'{self.user}, {self.role}'


class Category(models.Model):
    category_name = models.CharField(max_length=32, unique=True)

    def str(self):
        return self.category_name


class Course(models.Model):
    course_name = models.CharField(max_length=64)
    description = models.TextField()
    category = models.ManyToManyField(Category)
    author = models.ManyToManyField(Teacher)
    level = models.CharField(max_length=32, choices=STATUS_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    TYPE_CHOICES = (
        ('бесплатный', 'бесплатный'),
        ('платный', 'платный')
    )
    type_course = models.CharField(max_length=32, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course_certificate = models.BooleanField(default=True, )

    def str(self):
        return self.course_name


class Lesson(models.Model):
    title = models.CharField(max_length=64)
    video_url = models.URLField(null=True, blank=True)
    video = models.FileField(upload_to='course_videos', null=True, blank=True)
    content = models.FileField(upload_to='course_documents', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def str(self):
        return f'{self.course}, {self.title}'


class Assignment(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()
    due_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    students = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)

    def str(self):
        return self.title


class Exam(models.Model):
    title = models.CharField(max_length=32)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    end_time = models.DurationField()

    def str(self):
        return f'{self.title}, {self.course}'