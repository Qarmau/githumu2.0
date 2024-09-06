from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max

# Choices for various fields
YEARS = [
    (2020,2020),
    (2021,2021), 
    (2022, 2022),
    (2023, 2023),
    (2024, 2024)
]

GRADES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4)
]

ROOMS=[
    ('G','G'),
    ('B','B'),
    ('H','H'),
    ('S','S'),
    ('F','F'),
    ('A','A'),
    ('A1','A1'),
    ('A2','A2')

]

HOLIDAY_CHOICES = [
    ('April Holiday', 'April Holiday'),
    ('August Holiday', 'August Holiday'),
    ('December Holiday', 'December Holiday')
]

OFFICES = [
    ('CHIEF PRINCIPAL', 'CHIEF PRINCIPAL'),
    ('DEPUTY PRINCIPAL(ADMIN)', 'DEPUTY PRINCIPAL(ADMIN)'),
    ('DEPUTY PRINCIPAL(ACAD)', 'DEPUTY PRINCIPAL(ACAD)'),
    ('DEAN', 'DEAN'),
    ('HOD MATHEMATICS', 'HOD MATHEMATICS'),
    ('HOD SCIENCE', 'HOD SCIENCE'),
    ('HOD ENGLISH', 'HOD ENGLISH'),
    ('HOD KISWAHILI', 'HOD KISWAHILI'),
    ('HOD HUMANITIES', 'HOD HUMANITIES'),
    ('HOD TECHNICALS', 'HOD TECHNICALS'),
    ('HOD G&C', 'HOD G&C'),
    ('HOD CAREERS', 'HOD CAREERS'),
    ('HOD SPORTS', 'HOD SPORTS'),
    ('HOS', 'HOS')
]

GENDER_CHOICES = [
    ('Mr', 'Mr'),
    ('Mrs', 'Mrs'),
    ('Ms', 'Ms')
]

SUBJECTS = [
    ('BIO & CHEM', 'BIO & CHEM'),
    ('PHYS & CHEM', 'PHY & CHEM'),
    ('MATH & PHY', 'MATH & PHY'),
    ('MATH & CHEM', 'MATH & CHEM'),
    ('HIS & CRE', 'HIS & CRE'),
    ('GEO & HIS', 'GEO & HIS'),
    ('HIS & KIS', 'HIS & KIS'),
    ('KIS & CRE', 'KIS & CRE'),
    ('ENG/LIT', 'ENG/LIT'),
    ('MATH/COMP', 'MATH/COMP'),
    ('MATH/BUS', 'MATH/BUS'),
    ('HSC/BIO', 'HSC/BIO'),
    ('MATH/GEO', 'MATH/GEO'),
    ('HIS/P.E', 'HIS/P.E')
]

SUBJECTS_T = [
    ('MATHEMATICS', 'MATHEMATICS'),
    ('ENGLISH', 'ENGLISH'),
    ('KISWAHILI', 'KISWAHILI'),
    ('CHEMISTRY', 'CHEMISTRY'),
    ('PHYSICS', 'PHYSICS'),
    ('BIOLOGY', 'BIOLOGY'),
    ('BUSINESS STUDIES', 'BUSINESS STUDIES'),
    ('COMPUTER STUDIES', 'COMPUTER STUDIES'),
    ('AGRICULTURE', 'AGRICULTURE'),
    ('HOME SCIENCE', 'HOME SCIENCE'),
    ('HISTORY', 'HISTORY'),
    ('GEOGRAPHY', 'GEOGRAPHY'),
    ('CRE', 'CRE')
]

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='teacher')
    is_active = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token_expiration = models.DateTimeField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    def get_profile(self):
        if self.user_type == 'teacher':
            return self.teachingstaff
        elif self.user_type == 'administrator':
            return self.administrator
        else:
            return None

# Model Definitions
class Event(models.Model):
    title = models.CharField(max_length=50)
    date = models.DateTimeField()
    description = models.TextField()
    image = models.ImageField(upload_to='EVENT_images/', blank=True, null=True)
    video_url = models.FileField(upload_to='EVENT_videos/', blank=True, null=True)

    def __str__(self):
        return self.title

class News(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    video_url = models.FileField(upload_to='NEWS_videos/', blank=True, null=True)
    mynews = models.FileField(upload_to='news_info/', null=True, blank=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        return self.title
class CalendarEvent(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    event_type = models.CharField(max_length=10, choices=[('event', 'Event'), ('news', 'News')], default='event')
    related_id = models.IntegerField(null=True, blank=True)  # Allow null for existing entries

    def __str__(self):
        return f"{self.event_type}: {self.title}"

@receiver(post_save, sender=Event)
def create_calendar_event_from_event(sender, instance, created, **kwargs):
    if created:
        CalendarEvent.objects.create(
            title=instance.title,
            date=instance.date.date(),  # Convert DateTime to Date
            event_type='event',
            related_id=instance.id
        )
    else:
        # Update existing CalendarEvent if Event is modified
        calendar_event = CalendarEvent.objects.filter(event_type='event', related_id=instance.id).first()
        if calendar_event:
            calendar_event.title = instance.title
            calendar_event.date = instance.date.date()
            calendar_event.save()

@receiver(post_save, sender=News)
def create_calendar_event_from_news(sender, instance, created, **kwargs):
    if created:
        CalendarEvent.objects.create(
            title=instance.title,
            date=instance.date.date(),  # Convert DateTime to Date
            event_type='news',
            related_id=instance.id
        )
    else:
        # Update existing CalendarEvent if News is modified
        calendar_event = CalendarEvent.objects.filter(event_type='news', related_id=instance.id).first()
        if calendar_event:
            calendar_event.title = instance.title
            calendar_event.date = instance.date.date()
            calendar_event.save()

# Ensure the signals are connected
post_save.connect(create_calendar_event_from_event, sender=Event)
post_save.connect(create_calendar_event_from_news, sender=News)

from django.db import models
from django.core.validators import RegexValidator

class About(models.Model):
    history = models.TextField(
        help_text="Enter each point on a new line",
        blank=True,
        null=True,
        editable=False
    )
    population = models.IntegerField()
    school_motto = models.CharField(max_length=200)
    vision = models.TextField(blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    subjects_offered = models.TextField(
        help_text="Enter each subject on a new line",
        blank=True,
        null=True,
        editable=False
    )
    clubs_and_societies = models.TextField(
        help_text="Enter each club/society on a new line",
        blank=True,
        null=True,
        editable=False
    )
    contact_information = models.TextField(
        help_text="e.g. P.O BOX 001-00001, THIKA."
    )
    email = models.EmailField(
        help_text="Enter email to receive emails from users"
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+\d{1,3} \d{9}$',
                message='Phone number must be in the format: +<country_code> <9_digits>.'
            )
        ],
        help_text="Enter number to receive calls from users. Format: +<country_code> <9_digits>",
    )

    def __str__(self):
        return f"About - {self.school_motto}"

    class Meta:
        verbose_name = "About"
        verbose_name_plural = "About"

class Administrator(models.Model):
    name = models.CharField(max_length=20)
    title = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='admin_photos/')
    order = models.IntegerField(default=0)
    role = models.CharField(max_length=100, blank=True, choices=OFFICES)
    subjects = models.CharField(max_length=200, blank=True, choices=SUBJECTS)

    def __str__(self):
        return self.name

class TeachingStaff(models.Model):
    name = models.CharField(max_length=20)
    title = models.CharField(max_length=10, choices=GENDER_CHOICES)
    role = models.CharField(max_length=100, blank=True, choices=OFFICES)
    subjects = models.CharField(max_length=200, choices=SUBJECTS)
    photo = models.ImageField(upload_to='staff_photos/')
    order = models.IntegerField(default=0)
    is_administrator = models.BooleanField(default=False)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Administrator)
def create_teaching_staff(sender, instance, created, **kwargs):
    if created:
        TeachingStaff.objects.create(
            name=instance.name,
            title=instance.title,
            role=instance.role,
            subjects=instance.subjects,
            photo=instance.photo,
            order=instance.order,
            is_administrator=True
        )

# Ensure the signal is connected
post_save.connect(create_teaching_staff, sender=Administrator)


class Achievement(models.Model):
    year = models.IntegerField()
    university_admission_rate = models.FloatField()

class CoCurricularAward(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    description = models.TextField()
    photo = models.ImageField(upload_to='award_photos/')


class BackgroundImage(models.Model):
    image = models.ImageField(upload_to='background_images/')
    order = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk is None:  # Check if the instance is new
            # Get the current maximum order value
            max_order = BackgroundImage.objects.aggregate(Max('order'))['order__max']
            if max_order is not None:
                self.order = max_order + 1
            else:
                self.order = 1  # Set to 1 if there are no existing records

        super().save(*args, **kwargs)  # Call the original save method


class HolidayAssignment(models.Model):
    year = models.IntegerField(default=2024, choices=YEARS)
    title = models.CharField(max_length=200, choices=HOLIDAY_CHOICES)
    grade = models.IntegerField(default=1, choices=GRADES)
    subject = models.CharField(max_length=20, choices=SUBJECTS_T)
    file = models.FileField(upload_to='assignments/')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    download_count = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.title} - Grade {self.grade} - {self.subject}"



#gallery model
class Gallery(models.Model):
    CATEGORY_CHOICES = (
        ('events', 'Events'),
        ('School', 'Our School'),
        ('students', 'Students'),
        ('other', 'Staff'),
    )

    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=100)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Gallery"

    def __str__(self):
        return self.caption

#revision models
class AcademicYear(models.Model):
    year = models.IntegerField(choices=YEARS)

    def __str__(self):
        return str(self.year)

class Term(models.Model):
    name = models.CharField(max_length=20)  # e.g., "Term 1", "Term 2", "Term 3"

    def __str__(self):
        return self.name

class Grade(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g., "Form 1", "Form 2", "Form 3", "Form 4"

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100,choices=SUBJECTS_T)

    def __str__(self):
        return self.name

class PastPaper(models.Model):
    title = models.CharField(max_length=200,help_text="Enter the name of the exam to help students find it easier")
    file = models.FileField(upload_to='past_papers/')
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.grade} - {self.year} - {self.term}"

class RevisionMaterial(models.Model):
    title = models.CharField(max_length=200,help_text="Enter the name of the exam to help students find it easier")
    file = models.FileField(upload_to='revision_materials/')
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.grade} - {self.year} - {self.term}"

























class Stream(models.Model):
    name = models.CharField(max_length=100,choices=ROOMS)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='streams')

    def __str__(self):
        return f"{self.name} ({self.grade.name})"

class Student(models.Model):
    admission_number = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='students')
    kcpe=models.IntegerField()
    def __str__(self):
        return f"{self.name} - {self.admission_number}"
