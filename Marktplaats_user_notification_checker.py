#!/usr/bin/env python3
import requests, json, time

urlMP = 'https://www.marktplaats.nl/notifications/api/notifications?limit=10'
urlMPNotificationAPI = 'https://www.marktplaats.nl/notifications/api/notifications?limit=10&lastSeenNotificationId='
urlMPNotificationRM = 'https://www.marktplaats.nl/notifications/api/notifications/'
smsAPI = 'https://www.vodafone.nl/rest/secret?mobile=' #please don't abuse this, thank you!
phone_number = '31687654321'



headersMP = {
    "accept": "text/html,application/xhtml+xml,application/xml",
    "accept-encoding": "gzip, deflate, br",
    "cookie": "MpSslSecurity=0x00; MpSession=0x00; luckynumber=0x00",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}
headersSMSAPI = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}

"""
.:: RTFM
how?!:
Follow the user you want to get a notification about, unfollow all other users
Set this script in a crontab hourly/daily
SMS API GET sms from number 3000:
https://www.vodafone.nl/rest/secret?mobile=31687654321
Get notifications:
https://www.marktplaats.nl/notifications/api/notifications?limit=10
String must be present:
favoriteSellerPostedNewAds
Cookies required:
MpSession
MpSslSecurity
luckynumber
"""

class deserializeJSON(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

seconds = time.time()
local_time = time.ctime(seconds)
#print('Local time =' + str(local_time)) #dbg
#my hardware clock was facked, thin client 24/7/365 operation, parallel ata harddisk with 8 years power on time, bad sectors, system corruption!

if "19:00:" in local_time:
    try:
        r = requests.get(urlMP, headers=headersMP)
    except requests.exceptions.ConnectionError as e:
        print('Error while requesting notifications.')
        print(e)
    result = deserializeJSON(r.text)
    eventLabel = str(result.events[0]['label'])
    if result.events[0]['label'] != '' and eventLabel.rfind('favoriteSellerPostedNewAds_read') != -1:
        print('We found a new notification.')
        resp_LastNotificationId = deserializeJSON(r.text)
        sms = requests.get(smsAPI + phone_number, headers=headersSMSAPI)
        resp_dict = json.loads(sms.text)
        if resp_dict.get('status') == 200:
            notificationId = resp_LastNotificationId.notificationList[0]['id']
            print('Status 200, SMS was sent to end-user')
            #print('Mark last notification id as read & delete..')
            #print('Last notification id= ' + notificationId)
            #rmnoti = requests.delete(urlMPNotificationRM + notificationId, headers=headersMP)  # delete last notification
            #result = requests.get(urlMPNotificationAPI + notificationId, headers=headersMP)  # mark last notification as read
            #resp_LastMarkedNotification = deserializeJSON(result.text)
            #if resp_LastMarkedNotification.unreadNotificationsCount == 0:
            #    print('We have marked the last notification as read & deleted it.')
            #else:
            #    print('Warning: unable to remove last notification !')
        else:
            print('Error trying to signal end-user')
    else:
        print('No new notifications.')
