import datetime
import json
from .models import *
import requests as req


def logger_middleware(get_response):
    def middleware(request):
        logger(request)
        response = get_response(request)
        return response

    return middleware


def logger(request):
    avoided_strings = ['admin', 'log', 'rest', 'media']
    user = request.user
    ip = request.META.get('REMOTE_ADDR')
    # ip = '2.16.84.0'
    # ip = '207.228.238.7'
    dt = datetime.datetime.now()
    result = f'http://ip-api.com/json/{ip}'
    resp = req.get(result)
    j = json.loads(resp.text)
    if request.user is not None and not any(x in str(request.path) for x in avoided_strings):
        path = request.path
        if not request.user.is_anonymous:
            log = DashboardLog(ip=ip, user=user, requested_url=path, datetime=dt)
        else:
            log = DashboardLog(ip=ip, requested_url=path, datetime=dt)

    else:
        return
    if j['status'] == 'success':
        country = j['country']
        city = j['city']
        log.ip_city = city
        log.ip_country = country
    log.save()
