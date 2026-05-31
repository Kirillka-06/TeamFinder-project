from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('skills/', views.SkillsAutocompleteView.as_view(), name='skills_autocomplete'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
]