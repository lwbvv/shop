import requests

from django.conf import settings
from log import log
#통신을 하기 위한 토큰을 받아오는 역할
def get_token():
    access_data = {
        'imp_key': settings.IAMPORT_KEY,
        'imp_secret': settings.IAMPORT_SECRET
    }

    url = "https://api.iamport.kr/users/getToken"

    req = requests.post(url, data=access_data)
    access_res = req.json()

    if access_res['code'] is 0:
        return access_res['response']['access_token']

    else:
        return None

#아임포트에 미리 정보를 전달하여 어떤 주문 번호로 얼마를 결제할지 미리 전달하는 역할
def payments_prepare(order_id, amount, *args, **kwargs):
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid':order_id,
            'amount': amount
        }
        url = "https://api.iamport.kr/payments/prepare"
        headers = {
            'Authorization':access_token
            }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()

        if res['code'] is not 0:
            log("payments_prepare 통신오류:  ",res['code'] )
            raise ValueError("API 통신 오류")

    else:
        log("payments_prepare 토큰오류:  ",access_token )
        raise ValueError("토큰 오류")

#결제가 완료된 후에 실제 결제가 이루어진 것이 맞는지 확인할 떄 사용하는 함수
def find_transaction(order_id, *arg, **kwargs):
    access_token = get_token()
    if access_token:
        url = "https://api.iamport.kr/payments/find/"+order_id

        headers = {
            'Authorization':access_token
            }
        req = requests.post(url, headers=headers)
        res = req.json()

        if res['code'] is 0:
            context = {
                'imp_id':res['response']['imp_uid'],
                'merchant_order_id':res['response']['merchant_uid'],
                'amount':res['response']['amount'],
                'status':res['response']['status'],
                'type':res['response']['pay_method'],
                'receipt_url':res['response']['receipt_url']
            }
            return context

        else:
            return None
    else:
        raise ValueError("토큰 오류")
