from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
import json
from asgiref.sync import async_to_sync
from v1 import models

class PublishConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        self.accept()
        # 将当前连接对象添加到对应群聊中
        task_id = self.scope['url_route']['kwargs'].get("task_id")

        async_to_sync(self.channel_layer.group_add)(task_id, self.channel_name)

    def websocket_receive(self, message):
        task_id = self.scope['url_route']['kwargs'].get("task_id")
        text = message.get('text')
        if text == 'init':
            node_list = [{'key': "start", 'text': '开始', 'figure': 'Ellipse', 'color': "lightgreen"},
                         {'key': "download", 'parent': 'start', 'text': '下载代码', 'color': "lightgreen",
                          'link_text': '执行中...'},
                         {'key': "compile", 'parent': 'download', 'text': '本地编译', 'color': "lightgreen"},
                         {'key': "zip", 'parent': 'compile', 'text': '打包', 'color': "red", 'link_color': 'red'},
                         {'key': "c1", 'text': '服务器1', 'parent': "zip"}]
            start_node = models.Node.objects.create(text="开始",task_id=task_id)
            download_node = models.Node.objects.create(text="下载",task_id=task_id)
            upload_node = models.Node.objects.create(text="上传",task_id=task_id)

            
            # self.send(text_data=json.dumps({'code': 'init','data':node_list }))
            async_to_sync(self.channel_layer.group_send)(task_id, {
                'type': "my.send",
                'message': {'code': 'init', 'data': node_list},
            })

    def my_send(self,event):
        message = event.get('message')
        self.send(json.dumps(message))

    def websocket_disconnect(self, message):
        task_id = self.scope['url_route']['kwargs'].get("task_id")
        async_to_sync(self.channel_layer.group_discard)(task_id,self.channel_name)
        raise StopConsumer()
