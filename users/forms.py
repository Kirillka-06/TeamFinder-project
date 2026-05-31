import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=124)
    surname = forms.CharField(max_length=124)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


GITHUB_RE = re.compile(r'^https?://(www\.)?github\.com/', re.IGNORECASE)
PHONE_RE = re.compile(r'^(8\d{10}|\+7\d{10})$')


def normalize_phone(phone: str) -> str:
    '''Normalize phone: 8... -> +7...'''
    if phone.startswith('8'):
        return '+7' + phone[1:]
    return phone


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'avatar': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        self.fields['phone'].required = False
        self.fields['github_url'].required = False
        self.fields['about'].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return phone
        if not PHONE_RE.match(phone):
            raise forms.ValidationError(
                'Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX.'
            )
        normalized = normalize_phone(phone)
        qs = User.objects.filter(phone__in=[normalized, phone])
        if self.current_user:
            qs = qs.exclude(pk=self.current_user.pk)
        if qs.exists():
            raise forms.ValidationError('Этот номер телефона уже занят.')
        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url', '').strip()
        if not url:
            return url
        if not GITHUB_RE.match(url):
            raise forms.ValidationError('Ссылка должна вести на github.com.')
        return url


class CustomPasswordChangeForm(PasswordChangeForm):
    pass