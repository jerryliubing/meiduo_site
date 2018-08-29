import re

from rest_framework import serializers
from .models import User
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_email

from .models import Address
from . import constants

from goods.models import SKU


class UserCreateSerializer(serializers.Serializer):
    # 用户编号，只输出
    id = serializers.IntegerField(read_only=True)
    # 用户名
    username = serializers.CharField(
        min_length=5,
        max_length=20,
        error_messages={
            'min_length': "用户名不能少于5个字符",
            'max_length': "用户名不能大于20个字符",
        }
    )

    def validate_username(self, value):
        # 要求用户名中必须包含字母
        if not re.search(r'[a-zA-Z]',value):
            raise serializers.ValidationError("用户名中必须包含字母")

        # 验证用户名是否存在
        count = User.objects.filter(username=value).count()
        if count > 0:
            raise serializers.ValidationError('用户名存在')

        return value

    # 手机号
    mobile = serializers.CharField()

    def validate_mobile(self, value):
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        # 判断手机号是否存在
        count = User.objects.filter(username=value).count()
        if count > 0:
            raise serializers.ValidationError('手机号存在')

        return value

    # 密码
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': "密码不能少于5个字符",
            'max_length': "密码不能大于20个字符",
        }
    )
    # 重复密码
    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': "确认密码不能少于5个字符",
            'max_length': "确认密码不能大于20个字符",
        }
    )

    # 短信验证码,只输入
    sms_code = serializers.CharField(write_only=True)

    def validate_sms_code(self, value):
        # 验证短信验证码格式
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("短信验证码格式错误")

        return value

    # 是否同意协议
    allow = serializers.CharField(write_only=True)

    def validate_allow(self, value):
        if not value:
            raise serializers.ValidationError("请同意协议")
        return value

    # 验证多个属性
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("两次密码不一致")
        # 判断短信验证码是否正确
        redis_cli = get_redis_connection('verifiy_code')
        key = 'sms_code_' + attrs.get('mobile')
        sms_code_redis = redis_cli.get(key)
        sms_code_request = attrs.get('sms_code')
        if not sms_code_redis:
            raise serializers.ValidationError("验证码已过期")
        redis_cli.delete(key)  # 强制验证码失效
        if sms_code_redis.decode() != sms_code_request:
            raise serializers.ValidationError("短信验证码错误")

        return attrs

    # 增加代码1:token字段
    token = serializers.CharField(label="登录状态token",read_only=True)

    # 注册
    def create(self, validated_data):
        user = User()
        user.username=validated_data.get('username')
        user.mobile=validated_data.get('mobile')
        user.set_password(validated_data.get('password'))
        user.save()

        # 增加代码2:生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    # 之修改email方法
    def update(self, instance, validated_data):
        email = validated_data['email']
        instance.email = validated_data['email']
        instance.save()

        # 发送激活邮件
        # 代码会通知163,163再进行邮件发送，运行时间比较长，考虑加入异步celery

        # 生成验证链接
        verify_url = instance.generate_verify_email_url()
        # 发送验证邮件
        send_verify_email.delay(email, verify_url)

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)  # get方法查询,没查到会抛异常
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):
        """
        保存
        """
        # 将来序列化器使用时,报讯会调用这个方法
        # 将浏览记录保存到Redis中,使用list类型

        # self.context是一个字典,当视图调用序列化器时,会通过这个字典传递数据
        # 默认传递了request对象
        # 当jwt进行登录验证后,会将登录的用户对象user赋值给request对象:request.user=user
        user_id = self.context['request'].user.id
        # 获取商品编号
        sku_id = validated_data['sku_id']

        # 建立redis数据库连接
        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()

        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)

        pl.execute()

        return validated_data

