from django.db import models


# Create your models here.
class Server(models.Model):
    hostname = models.CharField(verbose_name="主机名", max_length=128)
    ip = models.CharField(verbose_name="ip", max_length=32)

    def __str__(self):
        return self.hostname

    class Meta:
        verbose_name_plural = "服务器"


class Project(models.Model):
    title = models.CharField(verbose_name='项目名', max_length=32)
    repo = models.CharField(verbose_name='仓库地址', max_length=128)

    env_choices = (
        ('prod', '正式'),
        ('test', '测试'),
    )
    env = models.CharField(verbose_name='环境',
                           max_length=16,
                           choices=env_choices,
                           default='test'
                           )

    path = models.CharField(verbose_name='线上项目地址', max_length=128)
    servers = models.ManyToManyField(verbose_name='关联服务器', to='Server')

    def __str__(self):
        return '%s-%s' % (self.title, self.env)

    class Meta:
        verbose_name_plural = "项目"


class DeployTask(models.Model):
    uid = models.CharField(verbose_name='标识', max_length=64)

    project = models.ForeignKey(verbose_name='项目', to="Project")
    tag = models.CharField(verbose_name='版本', max_length=32)

    status_choices = (
        (1, '待发布'),
        (2, '发布中'),
        (3, '成功'),
        (4, '失败'),
    )
    status = models.IntegerField(verbose_name='发布状态', choices=status_choices, default=1)

    before_download_script = models.TextField(verbose_name='下载前脚本', null=True, blank=True)
    after_download_script = models.TextField(verbose_name='下载后脚本', null=True, blank=True)
    before_deploy_script = models.TextField(verbose_name='发布前脚本', null=True, blank=True)
    after_deploy_script = models.TextField(verbose_name='发布后脚本', null=True, blank=True)


class HookTemplate(models.Model):
    """钩子脚本"""
    title = models.CharField(max_length=32, verbose_name='标题')
    content = models.TextField(verbose_name='脚本内容')
    # 针对不同阶段的钩子 做区分
    hook_type_choices = (
        (2, '下载前'),
        (4, '下载后'),
        (6, '发布前'),
        (8, '发布后'),
    )
    hook_type = models.IntegerField(verbose_name='钩子类型', choices=hook_type_choices)


class Node(models.Model):
    task = models.ForeignKey(verbose_name='发布任务', to='DeployTask')
    text = models.CharField(verbose_name='节点文字', max_length=32)
    status_choices = [
        ('lightgray', '待发布'),
        ('green', '成功'),
        ('red', '失败'),
    ]
    status = models.CharField(verbose_name='状态',max_length=16,choices=status_choices,default='lightgray')
    parent = models.ForeignKey(verbose_name='父节点',to='self',null=True,blank=True)
    server = models.ForeignKey(verbose_name='父节点',to='Server',null=True,blank=True)
