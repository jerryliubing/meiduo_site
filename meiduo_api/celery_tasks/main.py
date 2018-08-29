from celery import Celery

# 为celery使用django配置文件进行设置
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_api.settings")
# 创建celery应用
app = Celery('meiduo')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动注册celery任务
# 在指定的包中找tasks.py文件，在这个文件中找@app.task的函数，当做任务
app.autodiscover_tasks([
    'celery_tasks.sms',
    'celery_tasks.email',
    'celery_tasks.html',
])
