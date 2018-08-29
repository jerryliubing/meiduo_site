from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from .serializers import AreaSerializer, SubAreaSerializer


# Create your views here.


class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    行政区划信息
    """
    pagination_class = None  # 区划信息不分页
    # 由GenericAPIView提供
    # queryset = Area.objec
    # 当前支持两种操作:GET,
    # 查询列表GET,无pk--->所有的省
    # 查询一个,pk-------->查询地区及所有子集

    def get_queryset(self):
        """
        提供数据集
        """
        if self.action == 'list':
            # 查询所有的省信息
            return Area.objects.filter(parent=None)
        else:
            # 查询指定pk的数据,查询范围是如下指定
            return Area.objects.all()

    # 当进行GET,无pk时,查询所有省信息,使用AreaSerializer
    # 当进行GET,pk时,查询指定pk的数据并输出子地区信息,使用SubAreaSerializer
    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer
