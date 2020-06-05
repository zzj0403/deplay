from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
import json
from asgiref.sync import async_to_sync
from v1 import models
import threading
import subprocess
import os
from django.conf import settings
from git.repo import Repo
import shutil


def create_node(task_id, task_obj):
    node_queryset = models.Node.objects.filter(task_id=task_id)
    node_object_list = []
    if not node_queryset:

        start_node = models.Node.objects.create(text="开始", task_id=task_id)
        node_object_list.append(start_node)

        # 判断是否有下载前的勾子
        if task_obj.before_download_script:
            start_node = models.Node.objects.create(text="下载前", task_id=task_id, parent=start_node)
            node_object_list.append(start_node)

        download_node = models.Node.objects.create(text="下载", task_id=task_id, parent=start_node)
        node_object_list.append(download_node)

        if task_obj.after_download_script:
            download_node = models.Node.objects.create(text="下载后", task_id=task_id, parent=download_node)
            node_object_list.append(download_node)

        upload_node = models.Node.objects.create(text="上传", task_id=task_id, parent=download_node)
        node_object_list.append(upload_node)

        task_obj = models.DeployTask.objects.filter(pk=task_id).first()
        for server_obj in task_obj.project.servers.all():
            server_node = models.Node.objects.create(
                text=server_obj.hostname,
                task_id=task_id,
                parent=upload_node,
                server=server_obj,
            )
            node_object_list.append(server_node)
            if task_obj.before_deploy_script:
                server_node = models.Node.objects.create(
                    text='发布前',
                    task_id=task_id,
                    parent=server_node,
                    server=server_obj,
                )
                node_object_list.append(server_node)
            deploy_node = models.Node.objects.create(
                text='发布',
                task_id=task_id,
                parent=server_node,
                server=server_obj,
            )
            node_object_list.append(deploy_node)
            if task_obj.after_deploy_script:
                after_node = models.Node.objects.create(
                    text='发布后',
                    task_id=task_id,
                    parent=deploy_node,
                    server=server_obj,
                )
                node_object_list.append(after_node)
    else:
        node_object_list = node_queryset
    return node_object_list


def convert_obj_to_gojs(node_object_list):
    node_list = []
    for node_obj in node_object_list:
        temp = {
            'key': str(node_obj.pk),
            'text': node_obj.text,
            'color': node_obj.status
        }
        if node_obj.parent:
            temp['parent'] = str(node_obj.parent_id)
        node_list.append(temp)
    return node_list


class PublishConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        self.accept()
        # 将当前连接对象添加到对应群聊中
        task_id = self.scope['url_route']['kwargs'].get("task_id")

        async_to_sync(self.channel_layer.group_add)(task_id, self.channel_name)
        #
        node_onject_list = models.Node.objects.filter(task_id=task_id)
        if node_onject_list:
            node_list = convert_obj_to_gojs(node_onject_list)
            self.send(text_data=json.dumps({'code': 'init', 'data': node_list}))

    def deploy(self, task_id, task_obj):
        # 开始直接修改为绿色
        start_node = models.Node.objects.filter(text="开始", task_id=task_id).first()
        start_node.status = 'green'
        start_node.save()
        async_to_sync(self.channel_layer.group_send)(
            task_id,
            {'type': 'my.send', 'message': {'code': 'deploy', 'node_id': str(start_node.pk), 'color': 'green'}}
        )

        # 先通过代码文件自动创建出来

        project_name = task_obj.project.title
        uid = task_obj.uid
        script_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid, 'scripts')
        project_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid, project_name)
        package_folder = os.path.join(settings.PACKAGE_PATH, project_name)
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        if not os.path.exists(package_folder):
            os.makedirs(package_folder)

        # 下载前
        if task_obj.before_download_script:
            status = 'green'
            script_name = 'before_download_node.py'
            script_path = os.path.join(script_folder, script_name)
            with open(script_path, 'w', encoding='utf8')as f:
                f.write(task_obj.after_download_script)
            # 本地执行脚本文件
            try:
                subprocess.check_output('python  {0}'.format(script_name), shell=True, cwd=script_folder)
            except Exception as e:
                status = "red"
            # TODO:下载勾走脚本内容，本地执行
            before_download_node = models.Node.objects.filter(text="下载前", task_id=task_id).first()
            before_download_node.status = status
            before_download_node.save()
            async_to_sync(self.channel_layer.group_send)(
                task_id, {'type': 'my.send',
                          'message': {'code': 'deploy', 'node_id': str(before_download_node.pk), 'color': status}}
            )
            # 如果status 是red 就不先下去执行了
            if status == 'red':
                return

        # TODO:利用gitpython模块下载仓库
        status = 'green'
        try:
            Repo.clone_from(task_obj.project.repo, to_path=project_folder, branch='master')
        except Exception as e:
            status = 'red'

        download_node = models.Node.objects.filter(text="下载", task_id=task_id).first()
        download_node.status = status
        download_node.save()
        async_to_sync(self.channel_layer.group_send)(
            task_id,
            {'type': 'my.send', 'message': {'code': 'deploy', 'node_id': str(download_node.pk), 'color': status}}
        )
        if status == 'red':
            return

        if task_obj.after_download_script:
            status = 'green'
            script_name = 'after_download_script.py'
            script_path = os.path.join(script_folder, script_name)
            with open(script_path, 'w', encoding='utf8')as f:
                f.write(task_obj.after_download_script)
            # 本地执行脚本文件
            try:
                subprocess.check_output('python  {0}'.format(script_name), shell=True, cwd=script_folder)
            except Exception as e:
                status = "red"

            # TODO:下载勾走脚本内容，本地执行
            after_download_node = models.Node.objects.filter(text="下载后", task_id=task_id).first()
            after_download_node.status = status
            after_download_node.save()
            async_to_sync(self.channel_layer.group_send)(
                task_id, {'type': 'my.send',
                          'message': {'code': 'deploy', 'node_id': str(after_download_node.pk), 'color': status}}
            )
            if status == 'red':
                return

        # TODO:上传
        upload_node = models.Node.objects.filter(text="上传", task_id=task_id).first()
        upload_node.status = 'green'
        upload_node.save()
        async_to_sync(self.channel_layer.group_send)(
            task_id,
            {'type': 'my.send', 'message': {'code': 'deploy', 'node_id': str(upload_node.pk), 'color': 'green'}}
        )

        # 服务器多台
        for server_obj in task_obj.project.servers.all():
            # 创建代码
            # status = 'green'
            # try:
            #     upload_folder_path = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid)
            #     # zip 打包
            #     if __name__ == '__main__':
            #         package_path = shutil.make_archive(
            #             base_name=os.path.join(package_folder, uid + '.zip'),
            #             format='zip',
            #             root_dir=upload_folder_path
            #         )
            #         # paramiko 模块
            # except Exception as e:
            #     status = 'red'
            server_node = models.Node.objects.filter(text=server_obj.hostname, task_id=task_id,
                                                     server=server_obj).first()
            server_node.status = 'green'
            server_node.save()
            async_to_sync(self.channel_layer.group_send)(
                task_id,
                {'type': 'my.send', 'message': {'code': 'deploy', 'node_id': str(server_node.pk), 'color': 'green'}}
            )
            # 下载后
            if task_obj.before_deploy_script:
                # TODO:下载后勾走脚本内容，本地执行

                before_download_node = models.Node.objects.filter(text="发布前", task_id=task_id,
                                                                  server=server_obj).first()
                before_download_node.status = 'green'
                before_download_node.save()
                async_to_sync(self.channel_layer.group_send)(
                    task_id, {'type': 'my.send',
                              'message': {'code': 'deploy', 'node_id': str(before_download_node.pk),
                                          'color': 'green'}}
                )

            # 发布
            deploy_node = models.Node.objects.filter(text="发布", task_id=task_id, server=server_obj).first()
            deploy_node.status = 'green'
            deploy_node.save()
            async_to_sync(self.channel_layer.group_send)(
                task_id,
                {'type': 'my.send', 'message': {'code': 'deploy', 'node_id': str(deploy_node.pk), 'color': 'green'}}
            )

            # 发布后
            if task_obj.after_deploy_script:
                # TODO:下载勾走脚本内容，本地执行
                after_download_node = models.Node.objects.filter(text="发布后", task_id=task_id,
                                                                 server=server_obj).first()
                after_download_node.status = 'green'
                after_download_node.save()
                async_to_sync(self.channel_layer.group_send)(
                    task_id, {'type': 'my.send',
                              'message': {'code': 'deploy', 'node_id': str(after_download_node.pk),
                                          'color': 'green'}}
                )

    def websocket_receive(self, message):
        task_id = self.scope['url_route']['kwargs'].get("task_id")
        task_obj = models.DeployTask.objects.filter(pk=task_id).first()
        text = message.get('text')
        if text == 'init':
            node_object_list = create_node(task_id, task_obj)
            # 构建 数据格式
            node_list = convert_obj_to_gojs(node_object_list)
            # self.send(text_data=json.dumps({'code': 'init','data':node_list }))
            async_to_sync(self.channel_layer.group_send)(task_id, {
                'type': "my.send",
                'message': {'code': 'init', 'data': node_list},
            })
        if text == 'deploy':
            # self.deploy(task_id, task_obj)
            thread = threading.Thread(target=self.deploy, args=(task_id, task_obj))
            thread.start()

    def my_send(self, event):
        message = event.get('message')
        self.send(json.dumps(message))

    def websocket_disconnect(self, message):
        task_id = self.scope['url_route']['kwargs'].get("task_id")
        async_to_sync(self.channel_layer.group_discard)(task_id, self.channel_name)
        raise StopConsumer()
