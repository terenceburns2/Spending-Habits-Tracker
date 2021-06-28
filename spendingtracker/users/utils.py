import requests, json


# Get the user's latest login record
def get_latest_login(user):
    return user.logs[-1]


# Get login information: email address, ip address, login timestamp and region
def get_ip_address(request):
    # Try to get the login region
    ip = ''
    region = ''
    try:
        result = request.headers['X-Forwarded-For']
        if result is None:
            result = request.headers['X-Real-IP']
        ip = result.split(',')[0]
        res = requests.get(f"http://ip-api.com/json/{ip}")
        # Transfer the response to json
        json_text = json.loads(res.text)
        if json_text['status'] == 'success':
            region += json_text['zip'] + ', ' + json_text['city'] + ', ' + json_text['country']
    except:
        print('Error: Cannot get IP address')
    return ip, region

