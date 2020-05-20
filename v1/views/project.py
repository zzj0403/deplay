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
    edit_server = models.Server.objects.filter(pk=edit_id).first()
    all_form_obj = ProjectModelForm(instance=edit_server)
    if request.method == 'POST':
        form_obj = ProjectModelForm(data=request.POST, instance=all_form_obj)
        if form_obj.is_valid():
            form_obj.save()  # 有无instance参数来判断到底是新增数据还是编辑数据
            return redirect('project_add')
    return render(request, 'from.html', locals())


def project_delete(request, delete_id):
    models.Project.objects.filter(pk=delete_id).delete()
    return JsonResponse({'status': True})