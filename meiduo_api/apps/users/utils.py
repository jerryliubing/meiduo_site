import re
from .models import User

from django.contrib.auth.backends import ModelBackend


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 验证username是手机号还是用户名
        # # 1.方法1
        # try:
        #     if re.match(r'^1[3-9]\d{9}$', username):
        #         # 如果是手机号，则与mobile属性对比
        #         user = User.objects.get(mobile=username)
        #     else:
        #         # 如果是用户名，则与username属性对比
        #         user = User.objects.get(username=username)
        # except:
        #     return None
        # else:
        #     # 如果查询到用户对象，则判断密码是否正确
        #     if user.check_password(password):
        #         return user
        #     else:
        #         return None

        # 优化-1
        try:
            # 如果是手机号，则与mobile属性对比
            user = User.objects.get(mobile=username)
        except:
            try:
                # 如果是用户名，则与username属性对比
                user = User.objects.get(username=username)
            except:
                return None
        # 如果查询到用户对象，则判断密码是否正确
        if user.check_password(password):
            return user
        else:
            return None

