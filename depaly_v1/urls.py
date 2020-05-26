"""depaly_v1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from v1.views import server,project,task
urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 服务器相关
    url(r'^server_list/', server.server_list, name='server_list'),
    url(r'^server_add/', server.server_add, name='server_add'),
    url(r'^server_edit/(?P<edit_id>\d+)/$', server.server_edit, name='server_edit'),
    url(r'^server_delete/(?P<delete_id>\d+)/$', server.server_delete, name='server_delete'),

    # 项目相关
    url(r'^project/list/$', project.project_list, name='project_list'),
    url(r'^project/add/$', project.project_add, name='project_add'),
    url(r'^project/edit/(?P<edit_id>\d+)/$', project.project_edit, name='project_edit'),
    url(r'^project/delete/(?P<delete_id>\d+)/$', project.project_delete, name='project_delete'),

    # 发布任务相关
    url(r'^task_list/(?P<project_id>\d+)/$',task.task_list,name='task_list'),
    url(r'^task_add/(?P<project_id>\d+)/$',task.task_add,name='task_add'),

    # 获取脚本内容
    url(r'^hook/template/(?P<hook_id>\d+)/$',task.hook_template,name='hook_template')

]
