from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from projects.models import Skill
from .forms import CustomPasswordChangeForm, EditProfileForm, LoginForm, RegisterForm

User = get_user_model()


class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                password=form.cleaned_data['password'],
            )
            login(request, user)
            return redirect('/projects/list/')
        return render(request, 'users/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('/projects/list/')
            form.add_error(None, 'Неверный имейл или пароль')
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/projects/list/')


class UserListView(ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('id')


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'


class EditProfileView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def get(self, request):
        form = EditProfileForm(instance=request.user, current_user=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user, current_user=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
        return render(request, 'users/edit_profile.html', {'form': form})


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def get(self, request):
        return render(request, 'users/change_password.html', {'form': CustomPasswordChangeForm(request.user)})

    def post(self, request):
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f'/users/{request.user.id}/')
        return render(request, 'users/change_password.html', {'form': form})


class SkillsAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '')
        skills = (
            Skill.objects.filter(name__istartswith=q)
            .order_by('name')
            .values('id', 'name')[:10]
        )
        return JsonResponse(list(skills), safe=False)