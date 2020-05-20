from django.shortcuts import HttpResponse, render, redirect, reverse
from v1 import models
from django.http import JsonResponse
from v1.myforms.task import TaskModelForm


def task_list(request, project_id):
    task_list = models.DeployTask.objects.filter(project_id=project_id)
    project_obj = models.Project.objects.filter(pk=project_id).first()
    return render(request,'task_list.html',locals())