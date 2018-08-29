from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django_redis import get_redis_connection
import random
from utils.ytx_sdk.sendSMS import CCP
from celery_tasks.sms.tasks import sms_send

class SMSCodeView(APIView):
    # 当前输入结果是字典，没有对象所以不需要序列化操作
    # 接收手机号，在正则中已经验证，而且不涉及关系性数据库保存，所以不需要反序列化操作
    # 总结：不需要序列化器
    def get(self, request, mobile):
        '''
        接收手机号，发送短信验证码
        :param mobile: 手机号
        :return: 是否成功
        '''
        # 获取redis的连接
        redis_cli = get_redis_connection('verifiy_code')
        # 检查是否在60s内有发送记录
        sms_flag = redis_cli.get('sms_flag_' + mobile)  # 根据键，在redis中取值
        if sms_flag:
            raise serializers.ValidationError('请稍后在发送短信验证码')

        # 生成短信验证码
        sms_code = str(random.randint(100000, 999999))

        # 保存短信验证码与发送记录
        # 设置带有效期的数据，单位为秒
        # # 存验证码，300秒
        # redis_cli.setex('sms_code_' + mobile, 300, sms_code)
        # # 存发送标记，60秒
        # redis_cli.setex('sms_flag_' + mobile, 60, 1)

        # 优化redis交互，减少通信次数，管道pipline
        redis_pl = redis_cli.pipeline()
        redis_pl.setex('sms_code_' + mobile, 300, sms_code)
        redis_pl.setex('sms_flag_' + mobile, 60, 1)
        redis_pl.execute()

        # 发送短信
        # CCP.sendTemplateSMS(mobile,sms_code,5,1)
        # print(sms_code)

        # 调用celery任务:代理人会将这个任务添加到任务队列中
        sms_send.delay(mobile,sms_code,5,1)

        return Response({'message': 'OK'})
