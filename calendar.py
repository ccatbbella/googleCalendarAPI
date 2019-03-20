from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import plotly
import plotly.plotly as py
import plotly.graph_objs as go


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
FMT = '%H:%M'
l = [0,0,0,0,0,0,0,0,0,0,0,0]
colors = ["#9CF0F9", "7568EC", "#000000", "#4533E9", "EC8FA8", "#ffff00", "#F27C07","#458FFF", "#777281", "#000000", "#0A7C3B", "#E9162B"]
purpose = ['study', 'exercise', 'stub2', 'Office Hour' ,'section', 'meetings','self-reflection', 'everything else', 'mundane', 'stub9', 'luxury events', 'lecture']

def get_duration(event): #return duration of event as a number
    s = event['start'].get('dateTime')
    e = event['end'].get('dateTime')
    if s is None or e is None:
        #print("Event lasted over one days, cannot cal duration")
        return;
    sliced_s = s[11:16]
    sliced_e = e[11:16]
    tdelta = datetime.datetime.strptime(sliced_e, FMT) - datetime.datetime.strptime(sliced_s, FMT)
    duration = round(tdelta.total_seconds()/3600, 2)
    #print("Duration of event is ", duration, "hr")
    return duration

def main():
    #google calendar API setup stuff
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    
    #plotly setup stuff for graphing
    plotly.tools.set_credentials_file(username='yixiaoyue', api_key='myAPIkey')
    
    # Calling the Calendar API
    now = datetime.datetime.today().isoformat() + 'Z'  # 'Z' indicates UTC time
    print("Reminder: get all events from start date morning to end date night")
    begin_date = input("Please enter the begin date in year-month-date format(add 0 in front of single digit): ")
    end_date = input("Please enter the end date in year-month-date format: ")
    begin_date += "T1:00:00-07:00"
    end_date += "T23:00:00-07:00"
    events_result = service.events().list(calendarId='primary', timeMin=begin_date,timeMax=end_date,
                                         singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
        return;
    for event in events:
        
        #print("Event name is ", event['summary'])

        event_duration = get_duration(event)
        if event_duration is not None:
            if 'colorId' in event:
                #print("The color is", event['colorId'])
                color_int = int(event['colorId'])
                l[color_int] += event_duration
            else:
                #print("This event has default color")
                l[0] += event_duration

    
    '''
    print("Event hour summary as follows: ")
    for i in range(len(l)):
        print(purpose[i], ":", l[i], " hr")
    '''
    trace = go.Pie(labels=purpose, values=l, hoverinfo='value+label+percent', textinfo='value+label+percent', 
               textfont=dict(size=20),
               marker=dict(colors=colors, 
                           line=dict(color='#000000', width=2)))
    py.plot([trace], filename='calendar_summary:)')


if __name__ == '__main__':
    main()