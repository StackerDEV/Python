import requests, json, random, time, string, sys, socks, socket
from stem import Signal
from stem.control import Controller
from stem.connection import connect

# .:: RTFM
# Your "security" sucks! 
# tools used; all open source.
# date: 2017?

API_ENDPOINT = 'https://app-v2.appimin.com'
client_id = '3_59fbikiwl0g0cs88gkco4ksw84gcwo4gs044owkwc4w04c84w8'
client_secret = '66ym343hk5wc08sss4c0cko0w88gw0k4ckgcos4ksks4okococ'
client_useragent = 'okhttp/3.8.1' #ok.
AccessToken = '' #access token is valid for 3 days(72 hours, 4320 minutes)
LocalAccountDetails = ''


def setupTor():
	    controller = connect()
    if not controller:
        sys.exit(1)
    """
	change tor controller pw: tor --hash-password <YOUR_PASSWORD_HERE>
    wget TBB, edit torrc and add;
    ControlPort 8888
    HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE
    """
    controller = Controller.from_port(port=8888)
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150, True)
    socket.socket = socks.socksocket

def endpointLogin():
    global AccessToken
    API_SERVICE = '/oauth/v2/token'

    # data to be sent to api
    data = {'client_id': client_id,
            'client_secret': client_secret,
            'email': 'idiot@outlook.com',
            'grant_type': 'password',
            'password': '1234'}

    headers = {
        #'Content-Type': 'application/json',
        'User-Agent': client_useragent
    }
    proxies = {'http': 'socks5://localhost:9150'}
    r = requests.post(url=API_ENDPOINT+API_SERVICE, data=data, headers=headers, proxies=proxies)
    p = DeserializeJSON(r.text)
    if p.status == 200:
        print('We are logged in. Saving access token..')
        print(p.auth['access_token'])
        AccessToken = p.auth['access_token']
    elif p.status == 401:
        print('Auth service returned: Error 401 Unauthorized (Wrong username / password combo)')
    elif p.status == 403:
        print('!!! Houston, we have a problem !!!/n403 Forbidden error/nWe are probably banned or the Tor endpoint is blacklisted!')
    elif p.status == 503:
        print('Auth service returned: 503 Service Unavailable error.')

def endpointGetAPI(apiService, enAuth):
    API_SERVICE = apiService
    headers = {'User-Agent': client_useragent}
    if enAuth == True:
        headers['Authorization'] = 'Bearer ' + AccessToken
    proxies = {'http': 'socks5://localhost:9150'}
    r = requests.get(url=API_ENDPOINT+API_SERVICE, headers=headers, proxies=proxies)
    return(r.text);

def endpointGetUser():
    API_SERVICE = '/api/user'
    headers = {
        'Authorization': 'Bearer ' + AccessToken,
        'User-Agent': client_useragent
    }
    proxies = {'http': 'socks5://localhost:9150'}
    r = requests.get(url=API_ENDPOINT+API_SERVICE, headers=headers, proxies=proxies)
    p = DeserializeJSON(r.text)
    tickets = p.extra_data['tickets_won']
    print('This account has won ' + str(tickets)+ ' tickets.')

def endpointRegisterDevice():
    API_SERVICE = '/api/device/register' #POST
    #"deivce_id": 11 lenght A-Z 0-9 FirebaseInstanceId (random per account)
    #"location_status: 3
    #"platform_identifier": 2
    #"push_status": 2
def endpointGetGames():
    print('')
def endpointPlayGames():
    print('')
def endpointGetUserPrices():
    API_SERVICE = '/api/user/prizes'
    headers = {
        'Authorization': 'Bearer ' + AccessToken,
        'User-Agent': client_useragent
    }
    proxies = {'http': 'socks5://localhost:9150'}
    r = requests.get(url=API_ENDPOINT+API_SERVICE, headers=headers, proxies=proxies)
    p = DeserializeJSON(r.text)
    print('We have collected the prizes..')
def endpointRedeemTickets():
    print('')
def endpointGetAppVersion():
    API_SERVICE = '/api/app_settings'
    headers = {
        'User-Agent': client_useragent
    }
    proxies = {'http': 'socks5://localhost:9150'}
    r = requests.get(url=API_ENDPOINT+API_SERVICE, headers=headers, proxies=proxies)
    p = DeserializeJSON(r.text)
    if p.app_settings['app_version'] == '4.5' and p.app_settings['are_we_happy'] == True:
        print('Version check passed.')
    else:
        print('NEW version found or service not happy with endpoint.')
        sys.exit(0)

def readAccounts():
    global LocalAccountDetails
    file = open('accounts.txt', 'r+')
    LocalAccountDetails = file.readline()
    Details = LocalAccountDetails.split(':')
    if Details.__len__() == 2:
        localFirebaseInstanceIdFile()
    else:
        print('Account missing password.')

def genUniqeFirebaseInstanceId():
    InstanceId = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(11))
    return InstanceId;

def localFirebaseInstanceIdFile():
    InstanceId = genUniqeFirebaseInstanceId()
    with open('instanceids.txt', 'r+') as f:
        for line in f:
            if line.strip('\n') == InstanceId:
                genUniqeFirebaseInstanceId()
        f.write(InstanceId + '\n')
    return InstanceId;

def generateTimeStamp():
    return int(round(time.time()));

def TestTimeStamp():
    return time.time();

def renewExitnode():
	controller.authenticate('password')
	controller.signal(Signal.NEWNYM)

class DeserializeJSON(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

print('.:: Automation is the future')
setupTor()
#endpointLogin()
#delay = random.randrange(1, 10)
#print('Sleeping for ' + str(delay) + ' seconds (humanifying request)') # wireshark 1:1 traffic, wanna play a game? Catch me if you can.
#time.sleep(delay)
#endpointGetUser()
#endpointGetUserPrices()
#endpointGetAppVersion()
#print(localFirebaseInstanceIdFile())
#readAccounts()
#p = DeserializeJSON(endpointGetAPI('/api/app_settings', False))
#if p.app_settings['app_version'] == '4.5' and p.app_settings['are_we_happy'] == True:
#    print('Version check passed.')
#else:
#    print('NEW version found or service not happy with Tor exitnode.')
#    renewExitnode()
#.... play games
print(generateTimeStamp())


