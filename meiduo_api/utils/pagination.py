from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    # 默认每页显示几条数据
    page_size = 2
    # 在url地址中参数的名称?page_size=100
    page_size_query_param = 'page_size'
    # 每页最大数据条数,如果参数中比这个值大,以这个值为准
    max_page_size = 20
