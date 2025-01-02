import requests
from django.conf import settings

def get_lat_lng(address):
    url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode'
    headers = {
        'X-NCP-APIGW-API-KEY-ID': settings.NAVER_CLIENT_ID,
        'X-NCP-APIGW-API-KEY': settings.NAVER_CLIENT_SECRET
    }
    params = {'query': address}
    
    response = requests.get(url, headers=headers, params=params)
    try:
        data = response.json()
        if 'addresses' in data:
            if data['addresses']:
                lat = data['addresses'][0]['y']
                lng = data['addresses'][0]['x']
                return lat, lng
            else:
                return None, None
        else:
            return None, None
    except KeyError:
        return None, None
