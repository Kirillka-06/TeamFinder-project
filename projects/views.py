import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import ProjectForm
from .models import Project, Skill


def _parse_body(request):
    '''Parse request body: JSON or form-data.'''
    ct = request.content_type or ''
    if 'application/json' in ct:
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return {}
    return request.POST


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        skill = self.request.GET.get('skill', '')
        if skill:
            qs = qs.filter(skills__name=skill)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['all_skills'] = Skill.objects.order_by('name')
        ctx['active_skill'] = self.request.GET.get('skill', '')
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'


class ProjectCreateView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def get(self, request):
        return self._render(request, ProjectForm(), is_edit=False)

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}/')
        return self._render(request, form, is_edit=False)

    def _render(self, request, form, is_edit):
        from django.shortcuts import render
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': is_edit})


class ProjectEditView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user != project.owner and not request.user.is_staff:
            return redirect(f'/projects/{project_id}/')
        return self._render(request, ProjectForm(instance=project))

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user != project.owner and not request.user.is_staff:
            return redirect(f'/projects/{project_id}/')
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project_id}/')
        return self._render(request, form)

    def _render(self, request, form):
        from django.shortcuts import render
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


class ProjectCompleteView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user != project.owner:
            return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
        if project.status != 'open':
            return JsonResponse({'status': 'error', 'message': 'Project is not open'}, status=400)
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


class ProjectToggleParticipateView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        user = request.user
        if user in project.participants.all():
            project.participants.remove(user)
            participating = False
        else:
            project.participants.add(user)
            participating = True
        return JsonResponse({'status': 'ok', 'participant': participating})


class SkillsAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '')
        skills = (
            Skill.objects.filter(name__istartswith=q)
            .order_by('name')
            .values('id', 'name')[:10]
        )
        return JsonResponse(list(skills), safe=False)


class ProjectSkillAddView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user != project.owner:
            return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)

        data = _parse_body(request)
        skill_id = data.get('skill_id')
        name = (data.get('name') or '').strip()
        created = False

        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)
        else:
            return JsonResponse({'status': 'error', 'message': 'skill_id or name required'}, status=400)

        added = skill not in project.skills.all()
        if added:
            project.skills.add(skill)

        return JsonResponse({'skill_id': skill.id, 'id': skill.id, 'name': skill.name, 'created': created, 'added': added})


class ProjectSkillRemoveView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def post(self, request, project_id, skill_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user != project.owner:
            return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
        skill = get_object_or_404(Skill, pk=skill_id)
        if skill not in project.skills.all():
            return JsonResponse({'status': 'error', 'message': 'Skill not in project'}, status=400)
        project.skills.remove(skill)
        return JsonResponse({'status': 'ok'})