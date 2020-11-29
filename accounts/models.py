from django.contrib.auth.models import AbstractUser
from django.db import models
from portpolio.settings import common
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.validators import RegexValidator


class User(AbstractUser):
    GENDER_CHOICE = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    website_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=13,
                                    validators=[RegexValidator(r"^010-?[0-9]\d{3}-?\d{4}$")])
                                                                 #정규표현식
    gender = models.CharField(max_length=80, choices=GENDER_CHOICE, null=True)
    user_photo = models.ImageField(
        blank=True, null=True, upload_to='accounts/%y%m')
    follower_set = models.ManyToManyField("self", blank=True)
    following_set = models.ManyToManyField("self", blank=True)
    

    @property
    def name(self):
        return (f"{self.first_name} {self.last_name}")

    def send_welcome_email(self):
        title = render_to_string(
            'accounts/welcome_subject.txt',{'user':self})
        context = render_to_string(
            'accounts/welcome_context.txt',{'user':self})
        sender_email = "leepl37@naver.com"
        send_mail(title, context, sender_email, [
                  self.email], fail_silently=False),
