import requests, time, sys, socks, socket
from stem import Signal
from stem.control import Controller
from stem.connection import connect
#from selenium.common.exceptions import TimeoutException

if __name__ == '__main__':
    controller = connect()
    if not controller:
        sys.exit(1)
    """
    wget TBB, edit torrc and add;
    ControlPort 1337
    HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE
    """
    controller = Controller.from_port(port=1337)

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150, True)
    socket.socket = socks.socksocket

def removeTorSockProxy():
    #change proxy to default for geckodriver controller which also uses socks!
    socks.set_default_proxy()

def renew_tor():
    controller.authenticate('password')
    controller.signal(Signal.NEWNYM)

def verifyTor():
    controller.authenticate('password')
    result = '[OK] Tor is running version %s' % controller.get_version()
    controller.close()
    getmyip(1)
    connectTor()
    getmyip(2)
    removeTorSockProxy()
    if myip == torexitip:
        return '[WARNING] Tor is not working properly!'
        sys.exit()
    return result

def getmyip(type):
    global myip, torexitip
    r = requests.Session()
    page = r.get('http://icanhazip.com')
    if type == 1:
        myip = page.text
    else:
        torexitip = page.text

def webdriverAutomation(url):
    from selenium import webdriver
    #from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    #binary = FirefoxBinary("webdriver.firefox.bin", "%PROGRAMFILES%\Mozilla Firefox\firefox.exe")
    #driver = webdriver.Firefox(executable_path=r"C:\\geckodriver.exe")
    #use above if you don't have the system environment variable for chromedriver/geckodriver
    driver = webdriver.FirefoxProfile()
    driver.set_preference('network.proxy.type', 1)
    driver.set_preference('network.proxy.socks', '127.0.0.1')
    driver.set_preference('network.proxy.socks_port', 9150)
    driver = webdriver.Firefox(driver)
    driver.get(url)
    driver.implicitly_wait(2)
    while True:
        try:
            driver.find_element_by_xpath(".//*[@id='track-accept']/input[2]").click()
            break
        except:
            pass
    while True:
        try:
            driver.find_element_by_xpath(".//*[@id='flagging-popup-button']").click()
            time.sleep(4)
            driver.find_element_by_xpath(".//*[@id='reason-8']").click()
            driver.find_element_by_xpath(".//*[@id='flagging-form-submit-button']").click()
            time.sleep(4)
            break
        except:
            pass
    driver.close()

print('|------------------------------------|')
print('|    Chooched her last 0.1           |')
print('|    flagging scams without effort & |')
print('|    make em disappear!              |')
print('|------------------------------------|')
print(verifyTor())
url = str(input('Enter url: '))
runtime = int(input('How many times to run?: '))
for i in range(runtime):
    try:
        #some exitnodes don't repond or have reponse time beyond 300000ms !
        webdriverAutomation(url)
    except:
        pass
    print('Renewing tor exitnode:')
    renew_tor()
    print('Establishing new tor connection..')
print('We have completed. We finished with: ' + str(runtime) + ' runtimes.')
