from django.forms import ModelForm


class BaseModelForm(ModelForm):
    exclude_bootstrap = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(self.fields)  # OrderedDict([('hostname', <django.forms.fields.CharField object at 0x10715e198>)])
        for k, field in self.fields.items():
            if k in self.exclude_bootstrap:
                continue
            # 循环当前模型表中所有的字段对象 都添加一个class=form-control的属性
            field.widget.attrs['class'] = 'form-control'
