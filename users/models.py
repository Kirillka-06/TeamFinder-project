import io
import random
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    '#4A90D9', '#E67E22', '#2ECC71', '#9B59B6', '#E74C3C',
    '#1ABC9C', '#3498DB', '#F39C12', '#D35400', '#27AE60',
]


def generate_avatar(letter: str) -> ContentFile:
    size = 200
    color = random.choice(AVATAR_COLORS)
    img = Image.new('RGB', (size, size), color=color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
    except Exception:
        font = ImageFont.load_default()
    text = letter.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (size - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1]
    draw.text((x, y), text, fill='white', font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ContentFile(buf.read(), name=f'avatar_{uuid.uuid4()}.png')


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        # Generate avatar before saving
        avatar_content = generate_avatar(name[0] if name else 'U')
        user.avatar.save(avatar_content.name, avatar_content, save=False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/')
    phone = models.CharField(max_length=12, blank=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def __str__(self):
        return f'{self.name} {self.surname}'

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff
