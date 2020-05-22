from django.shortcuts import HttpResponse, render, redirect, reverse
from v1 import models
from django.http import JsonResponse
from v1.myforms.project import ProjectModelForm


def project_list(request):
    project_list = models.Project.objects.all()
    return render(request, 'project_list.html', locals())


def project_add(request):
    all_form_obj = ProjectModelForm()
    if request.method == "POST":
        form_obj = ProjectModelForm(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('project_list')
    return render(request, 'from.html', locals())


def project_edit(request, edit_id):
    edit_obj = models.Project.objects.filter(pk=edit_id).first()
    all_form_obj = ProjectModelForm(instance=edit_obj)

    if request.method == "POST":
        from_obj = ProjectModelForm(request.POST, instance=edit_obj)
        if from_obj.is_valid():
            from_obj.save()
            return redirect('project_list')
    return render(request, 'from.html', locals())


def project_delete(request, delete_id):
    models.Project.objects.filter(pk=delete_id).delete()
    return JsonResponse({'status': True})
