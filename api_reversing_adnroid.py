import time
import sys
import json
import random
import datetime
import socket #pip install pysocks
import requests
from stem import Signal
from stem.control import Controller
from stem.connection import connect

proxies = {'http': 'socks5://127.0.0.1:9150'} # tor
api_endpoint = 'www.xxxxxxx.nl'

"""
package: x
date: xx/xx/2021
why: test & see what is possible
toolkit: debian /w mitmproxy, rooted droid + xposed, recaf
tips: making safe api calls with retrofit and coroutines
"""

if __name__ == '__main__':
    controller = connect()
    if not controller:
        sys.exit(1)
    """
    change tor controller pw: tor --hash-password <YOUR_PASSWORD_HERE>
    wget TB, edit torrc and add;
    ControlPort 1337
    HashedControlPassword 16:C0A96F536E9C20586028862A720560EF1D3C696B3F003239372A6E4041 == password
    """
    controller = Controller.from_port(port=1337)

def forkFakeRegData():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    genlistreq = ['male/', 'female/']
    gengen = str(random.choice(genlistreq))
    try:
        res = requests.get('https://api.namefake.com/dutch-netherlands/' + gengen, proxies=proxies, headers=headers)
        res.raise_for_status()
        obj = json.loads(res.text.strip())

        x = str(obj['address']).split('\n')
        if x[0].__contains__('-'):
            address = x[0].rsplit(' ', 1)[0]
            xv = x[0].rsplit('-')  # remove useless suffix
            xxv = xv[0].rsplit(' ')
            housenumber = ''.join([i for i in xxv[xxv.__len__() - 1] if not i.isalpha()])
        else:  # handle different truely random formats
            address = x[0].rsplit(' ', 1)[0]
            housenumber = x[0].rsplit(' ', 1)[1]
        postal = x[1].split(' ')[0] + ' ' + x[1].split(' ')[1]
        town = x[1].replace(postal + ' ', '')

        dob = '/'.join(str(obj['birth_data']).split('-').__reversed__())  # correct format
        mailproviders = ['@gmail.com', '@hotmail.com', '@jahoo.com', '@icloud.com', '@mail.com', '@outlook.com',
                         '@aol.com']
        gen = 'mr' if not str(gengen).__contains__('female/') else 'mrs'
        email = obj['email_u'] + str(random.choice(mailproviders))
        firstname = str(obj['name']).split(' ', 1)
        lastname = firstname[1] if not firstname[1].find(' ') else str(firstname[1].rsplit(' ')[0])
        pwd = obj['password']
        renewExitNode()  # get a new exitnode..
        regdata = {'addition': '',
                   'address': address,
                   'birthdate': dob,
                   'email': email,
                   'firstName': firstname[0],
                   'gender': gen,
                   'house': housenumber,
                   'lastName': lastname,
                   'password': pwd,
                   'postalCode': postal,
                   'town': town}
        return regdata
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def signUpnDump(regdata): # dumping shit loads in dem database
    # missing cookie uid cannot be null -> header ?? mitmproxy & see recaf nl/idreams/data/entities/request/auth/SignUpRequest
    # token=x; refresh_token=x; userid=x; -> nl/idreams/data/entities/response/auth/AuthResponse
    encodejson = json.dumps(regdata);
    obj = json.loads(encodejson) # extraxting email key
    mailadr = obj['email']
    headers = {'Content-type': 'application/json; charset=UTF-8', 'Accept-encoding': 'gzip', 'User-agent': 'okhttp/4.9.1', 'cookie': mailadr}
    try:
        res = requests.post('https://' + api_endpoint + '/xxx/xx/xxxxx', data=json.dumps(regdata), proxies=proxies, headers=headers)
        res.raise_for_status()
        if res.status_code == 200:
            print('[Inf] Junk account injected in endpoint db')
            obj = json.loads(res.text.strip())
            bearerauth = {'access_token': obj['access_token'],
                    'refresh_token': obj['refresh_token'],
                    'customerId': obj['customerId'],
                    'email': mailadr}
            clientid = getClientID(bearerauth)
            getLoyaltynumbers(bearerauth, clientid)
        else:
            print('[Error in signUpnDump] ' + str(res.text))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def getClientID(brearer_tokens):
    encodejson = json.dumps(brearer_tokens);
    obj = json.loads(encodejson)
    headers = {'Content-type': 'application/json', 'Accept-encoding': 'gzip', 'User-agent': 'okhttp/4.9.1', 'cookie': 'token=' + obj['access_token'] + '; refresh_token=' +obj['refresh_token'] + '; userid=' + obj['email']}
    try:
        res = requests.get('https://' + api_endpoint + '/xxx/xx' + str(obj['email']) + '??xxx=x&x=xxx&lang=xxx&vendor=xxxxxx', proxies=proxies, headers=headers)
        res.raise_for_status()
        obj = json.loads(res.text.strip())
        if res.status_code == 200:
            print('[Inf] requested profile for UID')
            return str(obj['clientId'])
        else:
            print('[Error in getClientID] ' + str(res.text))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def getLoyaltynumbers(brearer_tokens, clientid):
    encodejson = json.dumps(brearer_tokens);
    obj = json.loads(encodejson)
    headers = {'Content-type': 'application/json', 'Accept-encoding': 'gzip', 'User-agent': 'okhttp/4.9.1', 'cookie': 'token=' + obj['access_token'] + '; refresh_token=' +obj['refresh_token'] + '; userid=' + obj['email']}
    try:
        res = requests.get('https://' + api_endpoint + '/xxx/xx/xxxxx/xxx/xxx' + str(clientid) + '?xxx=x&x=xxx&lang=xxx&vendor=xxxxxx', proxies=proxies, headers=headers)
        res.raise_for_status()
        if res.status_code == 200:
            print('[Inf] requested loyaltynumbers in endpoint')
            obj = json.loads(res.text.strip())
            print('|-------------------------------------|')
            print('| LoyaltyNumber found!                |')
            print('| Type: code 128 (barcode)            |')
            print('|-------------------------------------|')
            print('Code= ' + str(obj['loyaltyNumber']))
        else:
            print('[Error in getLoyaltynumbers] ' + str(res.text))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def renewExitNode():
    controller.authenticate("password")
    controller.signal(Signal.NEWNYM)

def verifyTor():
    controller.authenticate("password")
    result = '[OK] Tor is running version %s' % controller.get_version()
    print(result)
    controller.close()
    try:
        r_noproxy = requests.get('http://icanhazip.com/')
        r_proxy = requests.get('http://icanhazip.com/', proxies=proxies)
        if r_proxy.text.strip() == r_noproxy.text.strip():
            return '[WARNING] Tor is not working properly! ✘'
            sys.exit()
        else:
            print('[Tor] is working properly ✓')
        return result
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

print('|-------------------------------------|')
print('| Free? It’s usually a total rip-off  |')
print('|-------------------------------------|')
verifyTor()
dummydata = forkFakeRegData()
signUpnDump(dummydata)