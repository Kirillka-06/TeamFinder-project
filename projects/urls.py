from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='project_list'),
    path('create-project/', views.ProjectCreateView.as_view(), name='create_project'),
    path('skills/', views.SkillsAutocompleteView.as_view(), name='skills_autocomplete'),
    
    path('<int:project_id>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:project_id>/edit/', views.ProjectEditView.as_view(), name='edit_project'),
    path('<int:project_id>/complete/', views.ProjectCompleteView.as_view(), name='complete_project'),
    
    path('<int:project_id>/toggle-participate/', views.ProjectToggleParticipateView.as_view(), name='toggle_participate'),
    path('<int:project_id>/skills/add/', views.ProjectSkillAddView.as_view(), name='add_skill'),
    path('<int:project_id>/skills/<int:skill_id>/remove/', views.ProjectSkillRemoveView.as_view(), name='remove_skill'),
]