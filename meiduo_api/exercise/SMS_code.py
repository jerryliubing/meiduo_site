from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django_redis import get_redis_connection
import random
from utils.ytx_sdk.sendSMS import CCP


class SMSCodeView(APIView):
    # 不操作数据库，输入字典，没有对象不需要序列化操作
    # 接收手机号，验证在正则中已完成，不涉及关系性数据库保存，不需要反序列化
    # 不需要序列化器
    def get(self, request, mobile):
        '''
        :param mobile: 手机号
        :return: 是否成功
        '''
        # 获取redis连接
        redis_cli = get_redis_connection('verifiy_code')
        # 检查60s内是否有发送记录
        sms_flag = redis_cli.get('sms_flag_' + mobile)
        if sms_flag:
            raise serializers.ValidationError
        # 生成短信验证码
        sms_code = str(random.randint(100000, 999999))
        # 保存短信验证码与发送记录
        # # 1.优化前
        # # 存验证码，300秒
        # redis_cli.setex('sms_code_' + mobile, 300, sms_code)
        # # 存发送标记，60秒
        # redis_cli.setex('sms_flag_' + mobile, 60, 1)
        # 2.优化后
        redis_pl=redis_cli.pipeline()
        redis_pl.setex('sms_code_' + mobile, 300, sms_code)
        redis_pl.setex('sms_flag_' + mobile, 60, 1)
        redis_pl.execute()

        # 发送验证码短信
        # CCP.sendTemplateSMS(mobile,sms_code,5,1)
        print(sms_code)

        return Response({'message': 'OK'})
