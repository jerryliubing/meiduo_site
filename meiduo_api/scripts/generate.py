#!/usr/bin/env python
# 指定执行此py文件的命令为环境变量中的python
# /usr/bin/env表示在当前环境中查找python命令，当前为虚拟环境py3_django

"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_detail_html.py
"""
# 设置settis.py为环境变量
import sys

sys.path.insert(0, '../')

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_api.settings")

import django

django.setup()

# 编写环境代码,查询所有的商品,生成静态页面

from goods.models import SKU
from celery_tasks.html.tasks import generate_static_sku_detail_html

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)
