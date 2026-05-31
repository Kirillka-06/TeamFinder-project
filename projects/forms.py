import re

from django import forms
from .models import Project

GITHUB_RE = re.compile(r'^https?://(www\.)?github\.com/', re.IGNORECASE)


class ProjectForm(forms.ModelForm):
    STATUS_CHOICES = [('open', 'Открыт'), ('closed', 'Закрыт')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select)

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['github_url'].required = False

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url', '').strip()
        if not url:
            return url
        if not GITHUB_RE.match(url):
            raise forms.ValidationError('Ссылка должна вести на github.com.')
        return url
