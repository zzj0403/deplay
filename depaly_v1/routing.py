from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from v1 import consumers

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        url(r'^publish/(?P<task_id>\d+)/$', consumers.PublishConsumer)
    ])
})
