# Django
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db import models

# Models
from administration.models import Score


class OverrideUserManager(UserManager):

    def create_user(self, email, username=None, password=None, **extra_fields):
        """Create and save a user with the given username, email, and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        # username = GlobalUserModel.normalize_username(username)
        user = self.model(username=email, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, username=username, password=password, **extra_fields)
        return user


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    objects = OverrideUserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'


class CivilStatus(models.Model):
    c_status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self) -> str:
        return f'C_status:{self.c_status}'


class JobStatus(models.Model):
    has_job = models.BooleanField(default=False, null=False)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    salary = models.FloatField(null=True, blank=True)
    change_opt = models.BooleanField(default=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.company_name}, {self.salary}'


class Countries(models.Model):
    country_name = models.CharField(max_length=60)

    def __str__(self):
        return f'{self.country_name}'


class Cities(models.Model):
    city_name = models.CharField(max_length=60)
    country = models.ForeignKey(Countries, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.city_name}'


class Address(models.Model):
    address_line1 = models.CharField(max_length=150, blank=True, null=True)
    address_line2 = models.CharField(max_length=150, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.ForeignKey(Cities, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Countries, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.city}-{self.country}'


class Gender(models.Model):
    gender = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f'{self.gender}'


class ProcessStatus(models.Model):
    process_name = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f'{self.process_name}'


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    birthday = models.DateField(blank=True, null=True)
    score = models.ForeignKey(Score, null=True, blank=True, on_delete=models.SET_NULL)
    total_score = models.PositiveIntegerField(blank=True, null=True, default=0)
    gender = models.ForeignKey(Gender, null=True, blank=True, on_delete=models.SET_NULL)
    civil_status = models.ForeignKey(CivilStatus, null=True, blank=True, on_delete=models.SET_NULL)
    Address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    home_phone = models.CharField(max_length=15, blank=True, null=True)
    work_phone = models.CharField(max_length=15, blank=True, null=True)
    mobile_phone = models.CharField(max_length=15, blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    process_status = models.ForeignKey(ProcessStatus, null=True, blank=True, on_delete=models.SET_NULL)
    job_status = models.OneToOneField(JobStatus, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.score} user:{self.user}'


class LastGrade(models.Model):
    name = models.CharField(max_length=100)
    weight = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.name}-{self.weight}'


class GottenGrade(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name}'


class Education(models.Model):
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    last_grade = models.ForeignKey(LastGrade, null=True, on_delete=models.SET_NULL)
    gotten_grade = models.ForeignKey(GottenGrade, null=True, on_delete=models.SET_NULL)
    institution_name = models.CharField(max_length=100, null=True)
    year_end = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.institution_name}'


class ProfessionalExperience(models.Model):
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    start = models.DateField(null=True)
    end = models.DateField(null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.profile}, {self.company_name}'


class CambridgeLevel(models.Model):
    level = models.CharField(max_length=6)
    weight = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.level}-{self.weight}'


class Languages(models.Model):
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    language = models.CharField(max_length=25, unique=True)
    level = models.ForeignKey(CambridgeLevel, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.profile}, {self.language}'
