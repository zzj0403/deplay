from v1.myforms.base import BaseModelForm
from v1 import models
import datetime
from django import forms
import datetime


class TaskModelForm1(BaseModelForm):
    # 每一个钩子脚本都需要有一个下拉框  checkbox  文本框
    # 针对checkbox无需添加form-control的样式
    exclude_bootstrap = [
        'before_download_template',
        'after_download_template',
        'before_deploy_template',
        'after_deploy_template'
    ]

    before_download_select = forms.ChoiceField(required=False, label='下载前')
    before_download_title = forms.CharField(required=False, label='模板名称')
    before_download_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_download_select = forms.ChoiceField(required=False, label='下载后')
    after_download_title = forms.CharField(required=False, label='模板名称')
    after_download_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    before_deploy_select = forms.ChoiceField(required=False, label='发布前')
    before_deploy_title = forms.CharField(required=False, label='模板名称')
    before_deploy_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_deploy_select = forms.ChoiceField(required=False, label='下载后')
    after_deploy_title = forms.CharField(required=False, label='模板名称')
    after_deploy_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    class Meta:
        model = models.DeployTask
        fields = '__all__'
        # 有一些字段无需展示给用户看
        exclude = ['uid', 'project', 'status']

    def __init__(self, project_obj, *args, **kwargs):
        # 当你不知道函数或者方法有没有参数的时候 你就用*args,**kwargs
        super().__init__(*args, **kwargs)
        self.project_obj = project_obj
        self.init_hook()

    def init_hook(self):
        # self.fields  # 当前 对象里面包含的所有的字段数据
        # <option value="0">请选择</option>
        # 1 先添加默认的请选择
        before_download = [(0, '请选择'), ]
        # 2 再去钩子模版表中 查询对应类型的钩子数据
        extra_download = models.HookTemplate.objects.filter(hook_type=2).values_list('id', 'title')
        before_download.extend(extra_download)
        """
        values_list拿到的结果是列表套元祖
        values拿到的结果是列表套字典
        """
        self.fields['before_download_select'].choices = before_download
        after_download = [(0, '请选择')]
        extra_download = models.HookTemplate.objects.filter(hook_type=4).values_list('id', 'title')
        after_download.extend(extra_download)
        self.fields['after_download_select'].choices = after_download

        before_deploy = [(0, '请选择')]
        extra_download = models.HookTemplate.objects.filter(hook_type=6).values_list('id', 'title')
        before_deploy.extend(extra_download)
        self.fields['before_deploy_select'].choices = before_deploy

        after_deploy = [(0, '请选择')]
        extra_download = models.HookTemplate.objects.filter(hook_type=8).values_list('id', 'title')
        after_deploy.extend(extra_download)
        self.fields['after_deploy_select'].choices = after_deploy

    def create_uid(self):
        # luffy-test-v1-202011112311
        title = self.project_obj.title
        env = self.project_obj.env
        tag = self.cleaned_data.get('tag')  # 从校验通过的数据里面获取用户输入的版本信息
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return '%s-%s-%s-%s' % (title, env, tag, date)

    def save(self, commit=True):
        self.instance.uid = self.create_uid()
        self.instance.project_id = self.project_obj.pk
        super().save(commit=True)

        # 获取checkbox字段 如果有值 就操作模型表 没有就算了
        if self.cleaned_data.get('before_download_template'):
            title = self.cleaned_data.get("before_download_title")
            content = self.cleaned_data.get("before_download_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=2)

        if self.cleaned_data.get('after_download_template'):
            title = self.cleaned_data.get("after_download_title")
            content = self.cleaned_data.get("after_download_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=4)

        if self.cleaned_data.get('before_deploy_template'):
            title = self.cleaned_data.get("before_deploy_title")
            content = self.cleaned_data.get("before_deploy_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=6)

        if self.cleaned_data.get('after_deploy_template'):
            title = self.cleaned_data.get("after_deploy_title")
            content = self.cleaned_data.get("after_deploy_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=8)

    # 钩子函数   局部钩子  全局钩子
    def clean(self):
        # 获取保存为模版的checkbox值 如果有值 那么title就不能为空
        if self.cleaned_data.get('before_download_template'):
            title = self.cleaned_data.get("before_download_title")
            if not title:
                self.add_error('before_download_title', '请输入模版名称')

        if self.cleaned_data.get('after_download_template'):
            title = self.cleaned_data.get("after_download_title")
            if not title:
                self.add_error('after_download_title', '请输入模版名称')

        if self.cleaned_data.get('before_deploy_template'):
            title = self.cleaned_data.get("before_deploy_title")
            if not title:
                self.add_error('before_deploy_title', '请输入模版名称')

        if self.cleaned_data.get('after_deploy_template'):
            title = self.cleaned_data.get("after_deploy_title")
            if not title:
                self.add_error('after_deploy_title', '请输入模版名称')


class TaskModelForm(BaseModelForm):
    # 每个钩子都需要
    exclude_bootstrap = [
        'before_download_template',
        'after_download_template',
        'before_deploy_template',
        'after_deploy_template'
    ]
    before_download_select = forms.ChoiceField(required=False, label='下载前')
    before_download_title = forms.CharField(required=False, label='模板名称')
    before_download_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_download_select = forms.ChoiceField(required=False, label='下载后')
    after_download_title = forms.CharField(required=False, label='模板名称')
    after_download_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    before_deploy_select = forms.ChoiceField(required=False, label='发布前')
    before_deploy_title = forms.CharField(required=False, label='模板名称')
    before_deploy_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_deploy_select = forms.ChoiceField(required=False, label='下载后')
    after_deploy_title = forms.CharField(required=False, label='模板名称')
    after_deploy_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    class Meta:
        model = models.DeployTask
        fields = '__all__'
        exclude = ['uid', 'project', 'status']

    def __init__(self, project_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_obj = project_obj
        self.init_hook()

    def init_hook(self):
        before_download = [(0, '请选择'), ]
        # 2 再去钩子模版表中 查询对应类型的钩子数据
        extra_download = models.HookTemplate.objects.filter(hook_type=2).values_list('id', 'title')
        before_download.extend(extra_download)
        self.fields['before_download_select'].choices = before_download

        after_download = [(0, '请选择')]
        extra_download = models.HookTemplate.objects.filter(hook_type=4).values_list('id', 'title')
        after_download.extend(extra_download)
        self.fields['after_download_select'].choices = after_download

        before_deploy = [(0, '请选择')]
        extra_download = models.HookTemplate.objects.filter(hook_type=6).values_list('id', 'title')
        before_deploy.extend(extra_download)
        self.fields['before_deploy_select'].choices = before_deploy

        after_deploy = [(0, '请选择')]
        extra_download = models.HookTemplate.objects.filter(hook_type=8).values_list('id', 'title')
        after_deploy.extend(extra_download)
        self.fields['after_deploy_select'].choices = after_deploy

    def create_uid(self):
        title = self.project_obj.title
        env = self.project_obj.env
        tag = self.cleaned_data.get('tag')
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        return '%s_%s_%s_%s' % (title, env, tag, date)

    def save(self, commit=True):
        self.instance.uid = self.create_uid()
        self.instance.project_id = self.project_obj.pk
        super().save(commit=True)

        if self.cleaned_data.get('before_download_template'):
            title = self.cleaned_data.get("before_download_title")
            content = self.cleaned_data.get("before_download_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=2)

        if self.cleaned_data.get('after_download_template'):
            title = self.cleaned_data.get("after_download_title")
            content = self.cleaned_data.get("after_download_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=4)

        if self.cleaned_data.get('before_deploy_template'):
            title = self.cleaned_data.get("before_deploy_title")
            content = self.cleaned_data.get("before_deploy_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=6)

        if self.cleaned_data.get('after_deploy_template'):
            title = self.cleaned_data.get("after_deploy_title")
            content = self.cleaned_data.get("after_deploy_script")
            # 直接保存到钩子脚本模型表中
            models.HookTemplate.objects.create(title=title, content=content, hook_type=8)
