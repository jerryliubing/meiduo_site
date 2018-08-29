from rest_framework.routers import DefaultRouter
from . import views

# 视图集的路由生成
router = DefaultRouter()
router.register(r'areas', views.AreasViewSet, base_name='areas')

urlpatterns = []

urlpatterns += router.urls