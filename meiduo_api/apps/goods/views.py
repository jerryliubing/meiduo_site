from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter

from .serializers import SKUSerializer
from .models import SKU


class SKUListView(ListAPIView):
    """
    sku列表数据
    """
    serializer_class = SKUSerializer
    # 只针对当前查询实用过滤功能,所以不在settings.py中配置
    filter_backends = (OrderingFilter,)
    # 可排序的字段
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        # 获取分类编号***/?排序&分页&category_id=115
        # request.query_params.get()
        # 在APIView类中,定义了属性kwargs.类型是字典,表示请求的参数
        category_id = self.kwargs['category_id']
        # category_id = self.request.query_params.get('category_id')--->效果相同

        # 查询指定的分类的,上架的商品is_launched=True
        return SKU.objects.filter(category_id=category_id, is_launched=True)


from drf_haystack.viewsets import HaystackViewSet
from .serializers import SKUIndexSerializer


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
