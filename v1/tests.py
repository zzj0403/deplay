from django.test import TestCase

# Create your tests here.
import os
import sys
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "depaly_v1.settings")
    import django
    django.setup()


    from v1 import models
    task_obj = models.DeployTask.objects.filter(pk=13).first()
    project_obj = task_obj.project
    print(project_obj)