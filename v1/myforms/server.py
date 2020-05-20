from v1.myforms.base import BaseModelForm
from v1 import models


class ServerModelForm(BaseModelForm):
    class Meta:
        model = models.Server  # 指定待操作的模型表
        fields = '__all__'  # 展示所有字段到前端
