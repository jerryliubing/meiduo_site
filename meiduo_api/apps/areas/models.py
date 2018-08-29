from django.db import models

class Area(models.Model):
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    # 自关联:self
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')
    '''
    province=Area.objects.get(pk=1)
    province.parent:获取上级对象
    province.***_set:获取下级对象--改名-->province.subs
    '''

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name