from v1 import models
from v1.myforms.base import BaseModelForm


class ProjectModelForm(BaseModelForm):

    class Meta:
        model = models.Project  # 指定待操作的模型表
        fields = '__all__'  # 展示所有字段到前端

