from django.contrib import admin
from . import models
from celery_tasks.html.tasks import generate_static_sku_detail_html


# class SKUAdmin(admin.ModelAdmin):
#     list_per_page = 10
#     list_display = ['id', 'name', 'price', 'stock']
#
#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         # 当添加,修改时,会执行这个方法,完成原有操作,在下面添加额外代码
#         generate_static_sku_detail_html.delay(obj.id)
#
#     # def delete_model(self, request, obj):
#     #     super().delete_model(request, obj)
#     #     # 在下面添加额外代码
#     #     pass

# 商品SKU的管理类
class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)


# 商品SKU规格的管理类
class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        generate_static_sku_detail_html.delay(sku_id)


# 商品SKU图片的管理类
class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        generate_static_sku_detail_html.delay(sku_id)

admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
