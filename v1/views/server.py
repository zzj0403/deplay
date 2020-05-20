from django.shortcuts import HttpResponse, render, redirect, reverse
from v1 import models
from django.http import JsonResponse
from v1.myforms.server import ServerModelForm


def server_list(request):
    server_list = models.Server.objects.all()
    return render(request, 'server_list.html', locals())


def server_add(request):
    all_form_obj = ServerModelForm()
    if request.method == "POST":
        form_obj = ServerModelForm(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('server_list')
    return render(request, 'from.html', locals())


def server_edit(request, edit_id):
    edit_server = models.Server.objects.filter(pk=edit_id).first()
    all_form_obj = ServerModelForm(instance=edit_server)
    if request.method == 'POST':
        form_obj = ServerModelForm(data=request.POST, instance=all_form_obj)
        if form_obj.is_valid():
            form_obj.save()  # 有无instance参数来判断到底是新增数据还是编辑数据
            return redirect('server_list')
    return render(request, 'from.html', locals())


def server_delete(request, delete_id):
    models.Server.objects.filter(pk=delete_id).delete()
    return JsonResponse({'status': True})