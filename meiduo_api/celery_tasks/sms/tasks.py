from utils.ytx_sdk.sendSMS import CCP
from celery_tasks.main import app


@app.task(name='sms_send')
def sms_send(mobile, sms_code, expires, template_id):
    CCP.sendTemplateSMS(mobile, sms_code, expires, template_id)
    print(sms_code)


# @app.task
# def hello():
#     print('123')
