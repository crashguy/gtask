import requests


def sending_warning_sms(mobile, body):
    access_key_id = ""

    kwargs = {
        "Format": "JSON",
        "Version": "2016-09-27",
        "AccessKeyId": "",
        "Signature": "",
        "SignatureMethod": "HMAC-SHA1",
        "Timestamp": "",
        "SignatureVersion": "1.0",
        "SignatureNonce": "",

        "Action": "SingleSendSms",
        "SignName": "",
        "TemplateCode": "",
        "RecNum": "",
        "ParamString": "",
    }