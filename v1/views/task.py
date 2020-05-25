from django.shortcuts import HttpResponse, render, redirect, reverse
from v1 import models
from django.http import JsonResponse
from v1.myforms.task import TaskModelForm


def task_list(request, project_id):
    task_list = models.DeployTask.objects.filter(project_id=project_id)
    project_obj = models.Project.objects.filter(pk=project_id).first()
    return render(request, 'task_list.html', locals())


def task_add(request, project_id):

    project_obj = models.Project.objects.filter(pk=project_id).first()
    all_form_obj = TaskModelForm(project_obj=project_obj)
    if request.method == 'POST':
        form_obj = TaskModelForm(data=request.POST, project_obj=project_obj)
        if form_obj.is_valid():
            # 错误
            """
            (1048, "Column 'project_id' cannot be null")
            """
            # 解决反法
            # 1 直接手动写
            # form_obj.instance #当前数据对象
            # form_obj.instance.uid = 'zzz'
            # form_obj.instance.project_id = project_id
            # 2 重写save 方法

            form_obj.save()
            _url = reverse('task_list', args=(project_id,))
            return redirect(_url)
    return render(request, 'task_from.html', locals())
