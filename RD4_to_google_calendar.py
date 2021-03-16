from __future__ import print_function
import requests, json, base64, enum, datetime, time, sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# .:: RTFM
# holy handbook https://developers.google.com/calendar/v3/reference
# lat lon https://www.latlong.net/
# Google Auth : https://developers.google.com/calendar/quickstart/python
# tools used; ildasm, python, rooted droid phone

# .:: Target
# Android package name = nl.rd4.droid
# Tested on version release/3.2.6 GIT commit 8246df7 API v1.0
# Why: just because. why yall want my gps location?! Gtfo.

API_ENDPOINT = 'https://app.rd4.nl/nsi' # NsiApiBaseUrl
API_SERVICE = '/api/v1/wastecalendars' # Rd4.Mobile.Afvalapp.dll MD_TOKEN 0x0200009D namespace Rd4.Mobile.Afvalapp interface INsiApi GetWasteCalendars()
NsiApiKey = '201beffa86834d89a95cd52a302166a4' # Rd4.Mobile.Afvalapp.dll MD_TOKEN 0x020000BB, namespace Rd4.Mobile.Afvalapp class ApiKeys
ObjectCode_key = '0x00' # Android preference file nl.rd4.droid_preferences.xml objectCode_key (ObjectCode in the c# assembly)
Auth_Delimiter = ':' # Auth delimiter
WasteCardNr = 'MP12345' # Waste card number example MP12345
gps_LatLon = '52.375296,4.894478'
CalendarName = 'Waste Calendar'
Auth_full = ObjectCode_key + Auth_Delimiter + WasteCardNr
encodedBytes = base64.b64encode(Auth_full.encode('utf-8'))
Auth_full_encoded = str(encodedBytes, 'utf-8')
SCOPES = ['https://www.googleapis.com/auth/calendar']

calendar = {
    'summary': CalendarName,
    'timeZone': 'Europe/Amsterdam'
}

headers = {
    'Authorization': 'Basic ' + Auth_full_encoded,
    'API_KEY': NsiApiKey,
    'Accept': 'application/json'
}

class WasteCalendarType(enum.Enum):
    GeneralWaste = 0
    Bio = 1
    Paper = 2
    PruningWaste = 3
    Christmas = 4
    Plastic = 5
    BestBag = 6
    Nothing = 7

def main():
    creds = None
    global calendar_id

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    page_token = None
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == CalendarName:
            print('WARNING: Already existing calendar.')
            question = input("Continue and get possible duplicates? Y/N: ")
            if question.__contains__('N') or question.__contains__('n'):
                print("Remove '" + CalendarName + "' calendar manually. Go to https://calendar.google.com/calendar")
                sys.exit()
            print(calendar_list_entry['summary'] + ' ' + calendar_list_entry['id'])
            print("Using '" + calendar_list_entry['summary']+"'")
            calendar_id = calendar_list_entry['id']
            break
        else:
            created_calendar = service.calendars().insert(body=calendar).execute()
            print('New calendar created: ' + created_calendar['summary'] + ' ' + created_calendar['id'])
            calendar_id = created_calendar['id']
            break

    print('Preparing authentication id..')
    print('Requesting [GET] ' + API_SERVICE + ' on ' +  API_ENDPOINT)

    r = requests.get(url=API_ENDPOINT+API_SERVICE, headers=headers)
    p = deserializeJSON(r.text)
    if r.status_code == 401:
        print('Unauthorized 401, check ObjectCode_key or WasteCardNr')
    if r.status_code == 200:
        #print(r.text) dbg
        pickupCount = r.text.count("pickupDate")
        print('Found ' + str(pickupCount) + ' pickup dates to insert in calendar.')
        i = 0
        while i < pickupCount:
            #print('Pickup Date: ' + p._dict_[i]['pickupDate'].replace('T', ' Time: ') + ' Waste type: ' + str(WasteCalendarType(p._dict_[i]['pickupType']).__str__().replace('WasteCalendarType.', '')))
            eventSummary = str(WasteCalendarType(p._dict_[i]['pickupType']).__str__().replace('WasteCalendarType.', ''))
            eventSummary = renWasteType(eventSummary)
            event = {
                'summary': 'RD4: ' + eventSummary,
                'location': gps_LatLon,
                'start': {

                    'dateTime': p._dict_[i]['pickupDate'],
                    'timeZone': 'Europe/Amsterdam',
                },
                'end': {
                    'dateTime': p._dict_[i]['pickupDate'].replace('T00', 'T01'),
                    'timeZone': 'Europe/Amsterdam',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 300},
                        {'method': 'popup', 'minutes': 1440},
                    ],
                },
            }
            time.sleep(0.5) # Avoid googleapiclient.errors 403 Rate Limit Exceeded
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(p._dict_[i]['pickupDate'], eventSummary, '= added to calendar.')
            i += 1

    print("All pickup dates have been added, let's verify this.")
    print('Getting the upcoming 100 events')
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'], 'Reminders 1 :', event['reminders']['overrides'][0]['minutes'], 'Mins ', 'Reminders 2 :', event['reminders']['overrides'][1]['minutes'], 'Mins')

def renWasteType(arg):
    if arg == 'GeneralWaste':
        return 'Restafval'
    elif arg == 'Bio':
        return 'GFT en etensresten'
    elif arg == 'Paper':
        return 'Papierafval'
    elif arg == 'PruningWaste':
        return 'Snoeiafval op afspraak'
    elif arg == 'Christmas':
        return 'Kerstbomen'
    elif arg == 'Plastic':
        return 'PMD-verpakkingen'
    elif arg == 'BestBag':
        return 'BEST-tas'

class deserializeJSON(object):
    def __init__(self, j):
        self._dict_ = json.loads(j)

if __name__ == '__main__':
    print('.:: Automation is the future')
    main()
    print('Finished.')
